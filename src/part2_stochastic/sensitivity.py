"""
PART II -- Sensitivity analysis + Value of the Stochastic Solution (VSS).

SENSITIVITY (OAT) over:
  * storage scenario        -> low / base / high
  * production cost / m2    -> $20 (bulk) / $50 (base) / $86 (rush premium)
  * anticipatory waste      -> 1.0 (perfect guess) / 2.0 / 3.0 candidate teams
  * production lead time    -> 0 (same-day) / 1 (rush) days

VALUE OF THE STOCHASTIC SOLUTION (conceptual):
We report the split between anticipatory (stage-1) and reactive (stage-2)
cost as the storage/production parameters change. The managerial reading is
how the prudent pre-positioning cost trades off against reactive flexibility.

Outputs outputs/results/part2_sensitivity.csv
"""
from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl  # noqa: E402
from part2_stochastic.model import solve_stochastic  # noqa: E402


def run() -> list:
    rows = []

    for sc in ("low", "base", "high"):
        r = solve_stochastic(storage_scenario=sc, verbose=False)
        rows.append(("storage_scenario", sc, r["total_expected_cost"],
                     r["stage1_cost"], r["stage2_expected_cost"], r["n_forced"]))

    for c in (20.0, 50.0, 86.0):
        r = solve_stochastic(production_cost_per_m2=c, verbose=False)
        rows.append(("production_cost_per_m2", f"${c:.0f}", r["total_expected_cost"],
                     r["stage1_cost"], r["stage2_expected_cost"], r["n_forced"]))

    for w in (1.0, 2.0, 3.0):
        r = solve_stochastic(anticipatory_waste=w, verbose=False)
        rows.append(("anticipatory_waste", f"{w:.0f}x", r["total_expected_cost"],
                     r["stage1_cost"], r["stage2_expected_cost"], r["n_forced"]))

    for pd in (0.0, 1.0):
        r = solve_stochastic(production_days=pd, verbose=False)
        rows.append(("production_days", f"{pd:.0f}d", r["total_expected_cost"],
                     r["stage1_cost"], r["stage2_expected_cost"], r["n_forced"]))

    return rows


def main() -> None:
    rows = run()
    os.makedirs(dl.RESULTS_DIR, exist_ok=True)
    path = os.path.join(dl.RESULTS_DIR, "part2_sensitivity.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["parameter", "value", "total_expected_cost_usd",
                    "stage1_cost_usd", "stage2_cost_usd", "n_forced_anticipatory"])
        for p, v, tot, s1, s2, nf in rows:
            w.writerow([p, v, f"{tot:.0f}", f"{s1:.0f}", f"{s2:.0f}", nf])
    print(f"Wrote {path}\n")
    print(f"{'parameter':24} {'value':8} {'total':>11} {'stage1':>11} {'stage2':>11} {'forced':>7}")
    for p, v, tot, s1, s2, nf in rows:
        print(f"{p:24} {v:8} ${tot:>10,.0f} ${s1:>10,.0f} ${s2:>10,.0f} {nf:>7}")


if __name__ == "__main__":
    main()
