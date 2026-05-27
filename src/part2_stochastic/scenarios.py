"""
PART II -- Scenario generator (Monte-Carlo group-stage simulation).

GOAL
----
Part II is stochastic: we do NOT know which teams will play the 16 Round-of-32
matches, only the venues and dates. This script turns the known team strengths
(from betting odds) and the known group composition into a SAMPLE of plausible
scenarios. Each scenario fixes, for every R32 match, WHICH teams play there
(hence which nominative material -- flags, "Country A vs B" decals -- must be
produced and delivered to that venue by that date).

PIPELINE
--------
  1. Team strengths: implied probabilities from tournament-winner odds
     (user screenshots), normalised to remove the bookmaker margin.
  2. Group stage: for each of 50 Monte-Carlo runs, simulate every group with a
     strength-weighted ranking, producing 1st / 2nd / 3rd of each group.
  3. Best-third selection: rank the 12 third-placed teams, keep the best 8.
  4. Bracket mapping: place winners / runners-up / best-thirds into the 16
     fixed R32 slots (positions -> match -> venue -> date) per the FIFA table.
  5. Output one row per (scenario, match) with the two teams, venue, date.

These scenarios feed the two-stage stochastic model (model.py).

NOTE ON PROBABILITIES: we use tournament-winner odds as a STRENGTH PROXY, not
as qualification probabilities. The Monte-Carlo turns strength into
qualification frequencies. See docs/03_part2_model_spec.md.
"""
from __future__ import annotations

import csv
import os
import random

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
GENERATED_DIR = os.path.join(REPO_ROOT, "data", "generated")

# ---------------------------------------------------------------------------
# Team strengths: normalised implied probability from winner odds
# (user betting screenshots, 27 May 2026). Margin removed by normalisation.
# These are STRENGTH PROXIES.
# ---------------------------------------------------------------------------
ODDS = {
    "Spain": 5.50, "France": 6.00, "England": 8.00, "Argentina": 10, "Brazil": 10,
    "Portugal": 11, "Germany": 17, "Netherlands": 25, "Norway": 35, "Belgium": 45,
    "Colombia": 50, "Japan": 60, "Morocco": 60, "USA": 75, "Croatia": 100,
    "Ecuador": 100, "Mexico": 100, "Switzerland": 100, "Turkey": 100, "Uruguay": 100,
    "Senegal": 125, "Austria": 150, "Sweden": 150, "Scotland": 250, "Canada": 300,
    "Ivory Coast": 300, "Paraguay": 300, "Egypt": 400, "Czechia": 400,
    "South Korea": 400, "Algeria": 500, "Bosnia": 500, "Ghana": 600, "Australia": 700,
    "South Africa": 1000, "Saudi Arabia": 1000, "Iran": 1000, "Qatar": 1000,
    "DR Congo": 1000, "Tunisia": 1000, "Cape Verde": 2500, "Iraq": 2500,
    "Jordan": 2500, "New Zealand": 2500, "Uzbekistan": 2500, "Panama": 2500,
    "Curacao": 5000, "Haiti": 5000,
}

# 12 groups (official draw + resolved playoffs)
GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czechia"],
    "B": ["Canada", "Qatar", "Switzerland", "Bosnia"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["USA", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Tunisia", "Sweden"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Iraq", "Senegal", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["DR Congo", "Portugal", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# ---------------------------------------------------------------------------
# Round-of-32 bracket: 16 matches with positional matchup, venue, date.
# Positions: "1X"=winner of group X, "2X"=runner-up, "3rd[...]"=best third
# from the listed group pool. Venue node_id ties to the project network.
# ---------------------------------------------------------------------------
R32 = [
    dict(match=73, home="2A", away="2B", venue="STAD_LA", date="2026-06-28"),
    dict(match=74, home="1E", away="3rd:A,B,C,D,F", venue="STAD_BOS", date="2026-06-29"),
    dict(match=75, home="1F", away="2C", venue="STAD_MTY", date="2026-06-29"),
    dict(match=76, home="1C", away="2F", venue="STAD_HOU", date="2026-06-29"),
    dict(match=77, home="1I", away="3rd:C,D,F,G,H", venue="STAD_NY_NJ", date="2026-06-30"),
    dict(match=78, home="2E", away="2I", venue="STAD_DAL", date="2026-06-30"),
    dict(match=79, home="1A", away="3rd:C,E,F,H,I", venue="STAD_MEX", date="2026-06-30"),
    dict(match=80, home="1L", away="3rd:E,H,I,J,K", venue="STAD_ATL", date="2026-07-01"),
    dict(match=81, home="1D", away="3rd:B,E,F,I,J", venue="STAD_SF", date="2026-07-01"),
    dict(match=82, home="1G", away="3rd:A,E,H,I,J", venue="STAD_SEA", date="2026-07-01"),
    dict(match=83, home="2K", away="2L", venue="STAD_TOR", date="2026-07-02"),
    dict(match=84, home="1H", away="2J", venue="STAD_LA", date="2026-07-02"),
    dict(match=85, home="1B", away="3rd:E,F,G,I,J", venue="STAD_VAN", date="2026-07-02"),
    dict(match=86, home="1J", away="2H", venue="STAD_MIA", date="2026-07-02"),
    dict(match=87, home="1K", away="3rd:D,E,I,J,L", venue="STAD_KC", date="2026-07-03"),
    dict(match=88, home="2D", away="2G", venue="STAD_DAL", date="2026-07-03"),
]

GROUP_STAGE_END = "2026-06-27"


def _strengths() -> dict:
    raw = {k: 1.0 / v for k, v in ODDS.items()}
    s = sum(raw.values())
    return {k: v / s for k, v in raw.items()}


def simulate_group(teams: list, strength: dict, rng: random.Random) -> list:
    """
    Rank 4 teams by a strength-weighted random draw (Plackett-Luce style):
    repeatedly sample without replacement with probability proportional to
    strength. Returns ranking [1st, 2nd, 3rd, 4th].
    """
    remaining = list(teams)
    ranking = []
    while remaining:
        weights = [strength[t] for t in remaining]
        tot = sum(weights)
        r = rng.random() * tot
        acc = 0.0
        for t, wt in zip(remaining, weights):
            acc += wt
            if r <= acc:
                ranking.append(t)
                remaining.remove(t)
                break
        else:
            ranking.append(remaining.pop())
    return ranking


def simulate_tournament(strength: dict, rng: random.Random) -> dict:
    """One Monte-Carlo run -> resolves all 16 R32 matchups (team vs team)."""
    firsts, seconds, thirds = {}, {}, {}
    for g, teams in GROUPS.items():
        rank = simulate_group(teams, strength, rng)
        firsts[g], seconds[g], thirds[g] = rank[0], rank[1], rank[2]

    # best 8 of the 12 third-placed teams, ranked by strength proxy
    third_sorted = sorted(thirds.items(), key=lambda kv: -strength[kv[1]])
    best_thirds = third_sorted[:8]                 # list of (group, team)
    best_third_pool = {g: t for g, t in best_thirds}

    # assign best-thirds greedily to the 'away' 3rd-slots, respecting the
    # allowed group pool of each slot, strongest matches first.
    third_slots = [m for m in R32 if str(m["away"]).startswith("3rd:")]
    assigned = {}
    available = dict(best_third_pool)  # group -> team
    for slot in third_slots:
        pool = slot["away"].split(":")[1].split(",")
        # pick an available best-third whose group is in this slot's pool
        choice_group = next((g for g in pool if g in available), None)
        if choice_group is None and available:
            choice_group = next(iter(available))  # fallback
        if choice_group is not None:
            assigned[slot["match"]] = available.pop(choice_group)
        else:
            assigned[slot["match"]] = None

    def resolve(pos: str, match_id: int) -> str:
        if pos.startswith("1"):
            return firsts[pos[1]]
        if pos.startswith("2"):
            return seconds[pos[1]]
        if pos.startswith("3rd:"):
            return assigned.get(match_id)
        return pos

    out = {}
    for m in R32:
        out[m["match"]] = dict(
            home=resolve(m["home"], m["match"]),
            away=resolve(m["away"], m["match"]),
            venue=m["venue"], date=m["date"],
        )
    return out


def generate(n_scenarios: int = 50, seed: int = 42) -> str:
    strength = _strengths()
    rng = random.Random(seed)
    os.makedirs(GENERATED_DIR, exist_ok=True)
    path = os.path.join(GENERATED_DIR, "part2_scenarios.csv")
    prob = 1.0 / n_scenarios  # equiprobable scenarios (each MC run weight 1/N)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["scenario", "probability", "match", "home_team",
                    "away_team", "venue_node", "date"])
        for sc in range(n_scenarios):
            res = simulate_tournament(strength, rng)
            for mid, d in res.items():
                w.writerow([sc, prob, mid, d["home"], d["away"], d["venue"], d["date"]])
    return path


def main() -> None:
    path = generate(n_scenarios=50, seed=42)
    print(f"Wrote {path}")
    # quick sanity: show scenario 0
    import collections
    venue_count = collections.Counter()
    with open(path, encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["scenario"] == "0":
                venue_count[r["venue_node"]] += 1
    print("Scenario 0: 16 R32 matches across", len(venue_count), "venues")


if __name__ == "__main__":
    main()
