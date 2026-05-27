"""
PART I -- Location-Routing Problem (deterministic, cost-minimising MILP).

WHAT THIS MODEL DECIDES (simultaneously -- it is ONE integrated MILP)
---------------------------------------------------------------------
  1. Which ports to open, and how much volume travels FCL vs LCL.
  2. Which depots to open, and which port feeds which depot.
  3. Which depot serves which stadium (continuous flow).

TWO FREIGHT CLASSES
-------------------
  * LED  : heavy (~1000 kg/m3). FCL ONLY. Ships DIRECT port -> stadium
           (bypasses depots: 1 system/stadium, oversized/fragile, per README).
           Its WEIGHT (26 t/FEU) binds before its volume -> this is what makes
           the LED FEU count jump from ~16 (volume) to ~41 (weight).
  * SOFT : light (~460 kg/m3). FCL or LCL. Flows port -> depot -> stadium.
           Its VOLUME (67 m3/FEU) binds.

MULTIDIMENSIONAL CONTAINER CONSTRAINT (the heart of the model)
--------------------------------------------------------------
Each FEU has TWO simultaneous ceilings: 67 m3 AND 26 t. A container is full
as soon as EITHER limit is hit. We enforce both per class and per port.

OBJECTIVE = ocean (FCL + LCL + customs + handling)
          + depot fixed-opening
          + depot handling (per m3)
          + trucking port->depot (whole trucks)
          + trucking depot->stadium (whole trucks, soft)
          + trucking port->stadium (whole trucks, LED direct)

Storage is intentionally EXCLUDED in Part I: Cat-1 material transits, it is
not stored long term (see docs/04_assumptions_registry.md).

Solver: SCIP via OR-Tools pywraplp (MILP). See course KB, Session 6.
"""
from __future__ import annotations

import math
import os
import sys

from ortools.linear_solver import pywraplp

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl  # noqa: E402


def solve_lrp(
    led_direct: bool = True,
    use_depots: bool = True,
    enforce_weight: bool = True,
    allow_lcl: bool = True,
    verbose: bool = True,
):
    """
    Solve the Part I LRP.

    Parameters let us run alternative set-ups for the comparison/sensitivity:
      led_direct      : LED ships direct port->stadium (True) or via depot (False)
      use_depots      : route soft via depots (True) or direct port->stadium (False)
      enforce_weight  : enforce the 26 t weight ceiling (True) or volume-only (False)
      allow_lcl       : allow LCL for soft material (True) or FCL-only (False)
    """
    ports = dl.load_ports()
    depots = dl.load_depots()
    stadiums = dl.load_stadiums()
    demand = dl.load_stadium_demand()
    road = dl.load_road_edges()

    FEU = dl.FEU_VOLUME_M3
    PAY = dl.FEU_PAYLOAD_T
    TRUCK = dl.TRUCK_VOLUME_M3
    RHO_LED = dl.RHO_LED
    RHO_SOFT = dl.RHO_SOFT

    S = list(stadiums.keys())
    P = list(ports.keys())
    D = list(depots.keys())

    solver = pywraplp.Solver.CreateSolver("SCIP")
    if solver is None:
        raise RuntimeError("SCIP solver unavailable")
    INF = solver.infinity()

    # ---- decision variables -------------------------------------------------
    open_p = {p: solver.IntVar(0, 1, f"open_p[{p}]") for p in P}
    open_d = {d: solver.IntVar(0, 1, f"open_d[{d}]") for d in D}

    # containers per class per port
    feu_led = {p: solver.IntVar(0, INF, f"feu_led[{p}]") for p in P}
    feu_soft = {p: solver.IntVar(0, INF, f"feu_soft[{p}]") for p in P}
    # LCL only for ports that actually publish an LCL rate (Manzanillo has none)
    lcl_soft = (
        {p: solver.NumVar(0, INF, f"lcl_soft[{p}]")
         for p in P if ports[p]["lcl"] is not None}
        if allow_lcl else {}
    )

    # soft flow: port -> depot, depot -> stadium
    xs = {}  # (p,d)
    ntk_pd = {}
    yd = {}  # (d,s)
    ntk_ds = {}
    # LED flow: port -> stadium (direct) OR port->depot->stadium if led_direct False
    xl_ps = {}  # (p,s) direct led
    ntk_ps = {}
    xl_pd = {}  # (p,d) led via depot
    yl_ds = {}  # (d,s) led via depot

    for p in P:
        for d in D:
            if (p, d) in road:
                xs[p, d] = solver.NumVar(0, INF, f"xs[{p},{d}]")
                ntk_pd[p, d] = solver.IntVar(0, INF, f"ntk_pd[{p},{d}]")
    for d in D:
        for s in S:
            if (d, s) in road:
                yd[d, s] = solver.NumVar(0, INF, f"yd[{d},{s}]")
                ntk_ds[d, s] = solver.IntVar(0, INF, f"ntk_ds[{d},{s}]")

    if led_direct:
        for p in P:
            for s in S:
                if (p, s) in road:
                    xl_ps[p, s] = solver.NumVar(0, INF, f"xl_ps[{p},{s}]")
                    ntk_ps[p, s] = solver.IntVar(0, INF, f"ntk_ps[{p},{s}]")
    else:
        for p in P:
            for d in D:
                if (p, d) in road:
                    xl_pd[p, d] = solver.NumVar(0, INF, f"xl_pd[{p},{d}]")
        for d in D:
            for s in S:
                if (d, s) in road:
                    yl_ds[d, s] = solver.NumVar(0, INF, f"yl_ds[{d},{s}]")

    BIG = sum(d["vol_total"] for d in demand.values())

    # ---- (C1) demand satisfied, per class -----------------------------------
    for s in S:
        # soft
        solver.Add(
            solver.Sum(yd[d, s] for d in D if (d, s) in yd) == demand[s]["vol_soft"]
        )
        # led
        if led_direct:
            solver.Add(
                solver.Sum(xl_ps[p, s] for p in P if (p, s) in xl_ps)
                == demand[s]["vol_led"]
            )
        else:
            solver.Add(
                solver.Sum(yl_ds[d, s] for d in D if (d, s) in yl_ds)
                == demand[s]["vol_led"]
            )

    # ---- (C2) flow conservation at depots -----------------------------------
    for d in D:
        # soft in == soft out
        solver.Add(
            solver.Sum(xs[p, d] for p in P if (p, d) in xs)
            == solver.Sum(yd[d, s] for s in S if (d, s) in yd)
        )
        if not led_direct:
            solver.Add(
                solver.Sum(xl_pd[p, d] for p in P if (p, d) in xl_pd)
                == solver.Sum(yl_ds[d, s] for s in S if (d, s) in yl_ds)
            )

    # ---- (C3) multidimensional sea capacity per port ------------------------
    for p in P:
        # soft leaving port
        soft_out = solver.Sum(xs[p, d] for d in D if (p, d) in xs)
        cap_v = feu_soft[p] * FEU + (lcl_soft[p] if p in lcl_soft else 0)
        solver.Add(soft_out <= cap_v)
        if enforce_weight:
            cap_w = feu_soft[p] * PAY + (lcl_soft[p] * RHO_SOFT if p in lcl_soft else 0)
            solver.Add(soft_out * RHO_SOFT <= cap_w)

        # led leaving port (FCL only, no LCL term)
        if led_direct:
            led_out = solver.Sum(xl_ps[p, s] for s in S if (p, s) in xl_ps)
        else:
            led_out = solver.Sum(xl_pd[p, d] for d in D if (p, d) in xl_pd)
        solver.Add(led_out <= feu_led[p] * FEU)
        if enforce_weight:
            solver.Add(led_out * RHO_LED <= feu_led[p] * PAY)

    # ---- (C4) open coupling (big-M) -----------------------------------------
    for p in P:
        solver.Add(feu_soft[p] <= (BIG / FEU + 1) * open_p[p])
        solver.Add(feu_led[p] <= (BIG / FEU + 1) * open_p[p])
        if p in lcl_soft:
            solver.Add(lcl_soft[p] <= BIG * open_p[p])
    for d in D:
        out_d = solver.Sum(yd[d, s] for s in S if (d, s) in yd)
        if not led_direct:
            out_d = out_d + solver.Sum(yl_ds[d, s] for s in S if (d, s) in yl_ds)
        solver.Add(out_d <= BIG * open_d[d])

    # ---- (C5) whole-truck packing per arc -----------------------------------
    for (p, d) in xs:
        solver.Add(ntk_pd[p, d] * TRUCK >= xs[p, d]
                   + (xl_pd[p, d] if (not led_direct and (p, d) in xl_pd) else 0))
    for (d, s) in yd:
        load = yd[d, s] + (yl_ds[d, s] if (not led_direct and (d, s) in yl_ds) else 0)
        solver.Add(ntk_ds[d, s] * TRUCK >= load)
    if led_direct:
        for (p, s) in xl_ps:
            solver.Add(ntk_ps[p, s] * TRUCK >= xl_ps[p, s])

    # ---- objective ----------------------------------------------------------
    sea = solver.Sum(
        (feu_led[p] + feu_soft[p]) * (ports[p]["fcl"] + ports[p]["handling"])
        + open_p[p] * ports[p]["customs"]
        for p in P
    )
    if allow_lcl:
        sea = sea + solver.Sum(lcl_soft[p] * ports[p]["lcl"]
                               for p in P if ports[p]["lcl"] is not None and p in lcl_soft)
    depot_fixed = solver.Sum(open_d[d] * depots[d]["fixed"] for d in D) if use_depots else 0
    depot_hand = solver.Sum(
        solver.Sum(yd[d, s] for s in S if (d, s) in yd) * depots[d]["handling_m3"]
        for d in D
    )
    truck_pd = solver.Sum(ntk_pd[p, d] * road[(p, d)]["cost_per_truck"] for (p, d) in xs)
    truck_ds = solver.Sum(ntk_ds[d, s] * road[(d, s)]["cost_per_truck"] for (d, s) in yd)
    truck_ps = (solver.Sum(ntk_ps[p, s] * road[(p, s)]["cost_per_truck"] for (p, s) in xl_ps)
                if led_direct else 0)

    solver.Minimize(sea + depot_fixed + depot_hand + truck_pd + truck_ds + truck_ps)

    status = solver.Solve()
    if status != pywraplp.Solver.OPTIMAL:
        return dict(status="NOT_OPTIMAL", status_code=status)

    # ---- extract solution ---------------------------------------------------
    def val(v):
        return v.solution_value()

    total = solver.Objective().Value()
    sea_cost = sum((val(feu_led[p]) + val(feu_soft[p])) * (ports[p]["fcl"] + ports[p]["handling"])
                   + val(open_p[p]) * ports[p]["customs"] for p in P)
    if allow_lcl:
        sea_cost += sum(val(lcl_soft[p]) * ports[p]["lcl"]
                        for p in P if ports[p]["lcl"] is not None and p in lcl_soft)
    depot_fixed_cost = sum(val(open_d[d]) * depots[d]["fixed"] for d in D) if use_depots else 0
    depot_hand_cost = sum(sum(val(yd[d, s]) for s in S if (d, s) in yd) * depots[d]["handling_m3"]
                          for d in D)
    truck_pd_cost = sum(val(ntk_pd[p, d]) * road[(p, d)]["cost_per_truck"] for (p, d) in xs)
    truck_ds_cost = sum(val(ntk_ds[d, s]) * road[(d, s)]["cost_per_truck"] for (d, s) in yd)
    truck_ps_cost = (sum(val(ntk_ps[p, s]) * road[(p, s)]["cost_per_truck"] for (p, s) in xl_ps)
                     if led_direct else 0)

    feu_led_total = sum(val(feu_led[p]) for p in P)
    feu_soft_total = sum(val(feu_soft[p]) for p in P)

    result = dict(
        status="OPTIMAL",
        total_cost=total,
        cost_breakdown=dict(
            sea=sea_cost, depot_fixed=depot_fixed_cost, depot_handling=depot_hand_cost,
            truck_port_depot=truck_pd_cost, truck_depot_stadium=truck_ds_cost,
            truck_port_stadium_led=truck_ps_cost,
        ),
        ports_open={p: dict(feu_led=val(feu_led[p]), feu_soft=val(feu_soft[p]),
                            lcl_soft=val(lcl_soft[p]) if p in lcl_soft else 0.0)
                    for p in P if val(open_p[p]) > 0.5},
        depots_open=[d for d in D if val(open_d[d]) > 0.5],
        feu_led_total=feu_led_total,
        feu_soft_total=feu_soft_total,
        feu_total=feu_led_total + feu_soft_total,
        flows_soft_ds={(d, s): val(yd[d, s]) for (d, s) in yd if val(yd[d, s]) > 1e-6},
        flows_led_ps=({(p, s): val(xl_ps[p, s]) for (p, s) in xl_ps if val(xl_ps[p, s]) > 1e-6}
                      if led_direct else {}),
        setup=dict(led_direct=led_direct, use_depots=use_depots,
                   enforce_weight=enforce_weight, allow_lcl=allow_lcl),
    )

    if verbose:
        _print_result(result)
    return result


def _print_result(r: dict) -> None:
    print(f"\n=== PART I LRP  ({r['setup']}) ===")
    print(f"STATUS: {r['status']}")
    print(f"TOTAL COST = ${r['total_cost']:,.0f}")
    print(f"FEU: LED={r['feu_led_total']:.0f}  SOFT={r['feu_soft_total']:.0f}  "
          f"TOTAL={r['feu_total']:.0f}")
    print("\nPorts open:")
    for p, d in r["ports_open"].items():
        print(f"  {p:14} FEU_led={d['feu_led']:.0f}  FEU_soft={d['feu_soft']:.0f}  "
              f"LCL_soft={d['lcl_soft']:.1f} m3")
    print(f"Depots open: {r['depots_open']}")
    print("\nCost breakdown:")
    for k, v in r["cost_breakdown"].items():
        print(f"  {k:24} ${v:,.0f}")


if __name__ == "__main__":
    solve_lrp()
