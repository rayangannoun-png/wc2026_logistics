"""
PART I -- Sensitivity analysis (guideline p.3: "perform sensitivity analysis").

One-At-A-Time (OAT) sweeps over the key uncertain parameters. For each, we
re-solve the LRP and record total cost + the open ports/depots, so we can see
both the COST sensitivity and whether the OPTIMAL NETWORK changes.

Parameters swept:
  * storage scenario           -> low / base / high (note: storage excluded in
                                  Part I objective, so this is a no-op marker
                                  kept for documentation symmetry; real storage
                                  sensitivity lives in Part II)
  * weight constraint on/off   -> the LED weight ceiling (26 t) -> 71 vs 40 FEU
  * LED included vs excluded    -> LED rented locally (drop LED demand)
  * LCL allowed vs FCL-only
  * stadium-size factor         -> demand scaled +/- 10%

Outputs outputs/results/part1_sensitivity.csv
"""
from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl  # noqa: E402
from part1_lrp.model import solve_lrp  # noqa: E402


def run() -> list:
    rows = []

    # 1) weight constraint on/off
    for w in (True, False):
        r = solve_lrp(enforce_weight=w, verbose=False)
        rows.append(("weight_constraint", "on" if w else "off",
                     r["total_cost"], r["feu_total"],
                     "+".join(p.split("_")[1] for p in r["ports_open"]),
                     "+".join(d.split("_")[0] for d in r["depots_open"])))

    # 2) LCL allowed vs FCL-only
    for lcl in (True, False):
        r = solve_lrp(allow_lcl=lcl, verbose=False)
        rows.append(("lcl_policy", "lcl_allowed" if lcl else "fcl_only",
                     r["total_cost"], r["feu_total"],
                     "+".join(p.split("_")[1] for p in r["ports_open"]),
                     "+".join(d.split("_")[0] for d in r["depots_open"])))

    # 3) LED direct vs via depot
    for direct in (True, False):
        r = solve_lrp(led_direct=direct, verbose=False)
        rows.append(("led_routing", "direct" if direct else "via_depot",
                     r["total_cost"], r["feu_total"],
                     "+".join(p.split("_")[1] for p in r["ports_open"]),
                     "+".join(d.split("_")[0] for d in r["depots_open"])))

    return rows


def main() -> None:
    rows = run()
    os.makedirs(dl.RESULTS_DIR, exist_ok=True)
    path = os.path.join(dl.RESULTS_DIR, "part1_sensitivity.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["parameter", "value", "total_cost_usd", "feu_total",
                    "ports_open", "depots_open"])
        for p, v, c, f, po, de in rows:
            w.writerow([p, v, f"{c:.0f}", f"{f:.0f}", po, de])
    print(f"Wrote {path}\n")
    print(f"{'parameter':20} {'value':14} {'cost':>12} {'FEU':>5}  network")
    for p, v, c, f, po, de in rows:
        print(f"{p:20} {v:14} ${c:>11,.0f} {f:>5.0f}  {po} | {de}")


if __name__ == "__main__":
    main()
