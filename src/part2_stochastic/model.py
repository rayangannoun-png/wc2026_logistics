"""
PART II -- Two-stage stochastic program (time-critical nominative material).

TWO SUPPLY MODES (Voie 3)
-------------------------
For every R32 match, nominative material (flags, "Country A vs B" decals) can
be supplied in one of two ways:

  * REACTIVE (stage-2 recourse): produce locally AFTER the matchup is known,
    ship site->venue within the window. Cheaper (exact teams, no waste) BUT
    only feasible if  transit_time(site->venue) <= window - production_days.

  * ANTICIPATORY (stage-1 here-and-now): pre-print finished material BEFORE
    the group stage ends and pre-position it at the venue. Always feasible
    (no time constraint) BUT we do not yet know which teams qualify, so we
    must print for several candidate teams -> an over-production multiplier
    (waste factor). This is where the uncertainty really bites.

KEY RESULT THIS CAPTURES
------------------------
Several early R32 matches (LA on day +1, the Mexican venues) cannot be served
reactively in time. They FORCE anticipatory pre-positioning -- precisely the
role of the stage-1 decision. The model arbitrates reactive vs anticipatory
per match and per scenario.

OBJECTIVE = stage-1 (anticipatory production + pre-positioning storage)
          + E[ stage-2 reactive (production + trucking) ]

Solved as ONE large MILP (deterministic equivalent), 50 equiprobable
scenarios, SCIP. See docs/03_part2_model_spec.md.
"""
from __future__ import annotations

import csv
import os
import sys
from collections import defaultdict
from datetime import date

from ortools.linear_solver import pywraplp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl  # noqa: E402

# --- material & cost constants (see docs/04_assumptions_registry.md) --------
M2_PER_MATCH = 275.0
M2_TO_M3 = 0.00056 / 0.57
VOL_PER_MATCH_M3 = M2_PER_MATCH * M2_TO_M3

PRODUCTION_COST_PER_M2 = 50.0            # USD/m2 (US large-format, 2026 base)
PROD_COST_PER_M3 = PRODUCTION_COST_PER_M2 / M2_TO_M3
PRODUCTION_DAYS = 1.0                    # rush production lead time
ANTICIPATORY_WASTE = 2.0                 # print for ~2 candidate teams (over-prod)
WAIT_DAYS = 30                           # storage horizon for anticipatory stock
GROUP_STAGE_END = date(2026, 6, 27)
CHINA = "PROD_CHINA_SHANGHAI"


def _window_days(date_str: str) -> int:
    y, m, d = map(int, date_str.split("-"))
    return (date(y, m, d) - GROUP_STAGE_END).days


def load_scenarios():
    path = os.path.join(dl.GENERATED_DIR, "part2_scenarios.csv")
    scenarios = defaultdict(list)
    prob = {}
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            sc = int(r["scenario"])
            scenarios[sc].append(r)
            prob[sc] = float(r["probability"])
    return scenarios, prob


def solve_stochastic(
    production_cost_per_m2: float = PRODUCTION_COST_PER_M2,
    anticipatory_waste: float = ANTICIPATORY_WASTE,
    storage_scenario: str = "base",
    production_days: float = PRODUCTION_DAYS,
    verbose: bool = True,
):
    prod = dl.load_production_sites()
    road = dl.load_road_edges()
    storage = dl.load_storage_scenarios()
    scenarios, prob = load_scenarios()

    sites = [n for n in prod if n != CHINA]
    storage_cost = storage[storage_scenario]["cost_per_m3_day"]
    prod_cost_per_m3 = production_cost_per_m2 / M2_TO_M3

    def reactive_feasible(site, venue, window):
        e = road.get((site, venue))
        if e is None or e["transit_time_days"] is None:
            return False
        return e["transit_time_days"] <= (window - production_days)

    # Identify the set of distinct (match, venue) slots from the bracket; the
    # venue/date are scenario-independent, only the teams change. Anticipatory
    # pre-positioning is therefore a per-MATCH stage-1 decision.
    match_venue, match_window = {}, {}
    for sc, rows in scenarios.items():
        for r in rows:
            mid = int(r["match"])
            match_venue[mid] = r["venue_node"]
            match_window[mid] = _window_days(r["date"])
    matches = sorted(match_venue)

    solver = pywraplp.Solver.CreateSolver("SCIP")
    INF = solver.infinity()

    # ---- stage-1: anticipatory finished material pre-positioned per match ---
    # a[m] = volume of finished nominative material pre-positioned at venue of
    # match m, before results (covers match m in ANY scenario).
    a = {m: solver.NumVar(0, INF, f"a[{m}]") for m in matches}

    # ---- stage-2: reactive production per scenario/match/site ---------------
    z = {}
    for sc, rows in scenarios.items():
        for r in rows:
            mid = int(r["match"])
            venue = r["venue_node"]
            window = match_window[mid]
            for j in sites:
                if reactive_feasible(j, venue, window):
                    z[sc, mid, j] = solver.NumVar(0, INF, f"z[{sc},{mid},{j}]")

    # ---- (C1) each match served in each scenario: reactive + anticipatory ---
    for sc, rows in scenarios.items():
        for r in rows:
            mid = int(r["match"])
            reactive = [z[sc, mid, j] for j in sites if (sc, mid, j) in z]
            # anticipatory stock a[mid] is available in every scenario
            solver.Add(solver.Sum(reactive) + a[mid] >= VOL_PER_MATCH_M3)

    # ---- objective ----------------------------------------------------------
    # stage 1: anticipatory production (with waste) + storage of the stock
    stage1 = solver.Sum(
        a[m] * (anticipatory_waste * prod_cost_per_m3 + storage_cost * WAIT_DAYS)
        for m in matches
    )
    # stage 2: expected reactive (production + trucking), exact teams, no waste
    stage2_terms = []
    for sc, rows in scenarios.items():
        p = prob[sc]
        for r in rows:
            mid = int(r["match"])
            venue = r["venue_node"]
            for j in sites:
                if (sc, mid, j) in z:
                    truck_per_m3 = road[(j, venue)]["cost_per_truck"] / dl.TRUCK_VOLUME_M3
                    stage2_terms.append(p * (prod_cost_per_m3 + truck_per_m3) * z[sc, mid, j])
    stage2 = solver.Sum(stage2_terms)

    solver.Minimize(stage1 + stage2)
    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        return dict(status="NOT_OPTIMAL", status_code=status)

    def val(v):
        return v.solution_value()

    anticip = {m: val(a[m]) for m in matches if val(a[m]) > 1e-9}
    stage1_cost = sum(val(a[m]) * (anticipatory_waste * prod_cost_per_m3
                                   + storage_cost * WAIT_DAYS) for m in matches)
    stage2_cost = solver.Objective().Value() - stage1_cost

    # which matches are served purely anticipatory (no reactive option at all)
    reactive_possible = set()
    for (sc, mid, j) in z:
        reactive_possible.add(mid)
    forced_anticipatory = [m for m in matches if m not in reactive_possible]

    site_usage = defaultdict(float)
    for (sc, mid, j), var in z.items():
        if val(var) > 1e-9:
            site_usage[j] += prob[sc]

    result = dict(
        status="OPTIMAL",
        total_expected_cost=solver.Objective().Value(),
        stage1_cost=stage1_cost,
        stage2_expected_cost=stage2_cost,
        anticipatory_by_match=anticip,
        forced_anticipatory_matches=forced_anticipatory,
        n_forced=len(forced_anticipatory),
        site_usage_freq=dict(site_usage),
        vol_per_match_m3=VOL_PER_MATCH_M3,
        n_scenarios=len(scenarios),
        match_venue=match_venue,
        match_window=match_window,
        setup=dict(production_cost_per_m2=production_cost_per_m2,
                   anticipatory_waste=anticipatory_waste,
                   storage_scenario=storage_scenario,
                   production_days=production_days),
    )
    if verbose:
        _print(result)
    return result


def _print(r: dict) -> None:
    print(f"\n=== PART II STOCHASTIC ({r['setup']}) ===")
    print(f"STATUS: {r['status']}  |  scenarios: {r['n_scenarios']}")
    print(f"TOTAL EXPECTED COST = ${r['total_expected_cost']:,.0f}")
    print(f"  stage-1 (anticipatory prod + storage): ${r['stage1_cost']:,.0f}")
    print(f"  stage-2 (E[reactive prod + truck]):    ${r['stage2_expected_cost']:,.0f}")
    print(f"\nForced-anticipatory matches (no reactive site in time): "
          f"{r['n_forced']} -> {r['forced_anticipatory_matches']}")
    print("Matches pre-positioned anticipatorily (stage-1 > 0):")
    for m, v in sorted(r["anticipatory_by_match"].items()):
        venue = r["match_venue"][m]
        win = r["match_window"][m]
        print(f"  match {m:3} @ {venue:12} (window {win}d)  {v:.4f} m3")
    print("Reactive site usage frequency:")
    for j, f in sorted(r["site_usage_freq"].items(), key=lambda kv: -kv[1]):
        print(f"  {j:20} {100*f:.0f}% of scenario-matches")


if __name__ == "__main__":
    solve_stochastic()
