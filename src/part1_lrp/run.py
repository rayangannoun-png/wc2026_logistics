"""
PART I runner: solves the baseline LRP, exports flows and a cost summary,
and runs the alternative set-ups for the managerial comparison (guideline p.6:
"consider more than one instance / compare set-ups").

Run:  python -m src.part1_lrp.run    (from repo root)
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl  # noqa: E402
from part1_lrp.model import solve_lrp  # noqa: E402


def export_baseline(result: dict) -> None:
    os.makedirs(dl.RESULTS_DIR, exist_ok=True)

    # cost summary as JSON
    with open(os.path.join(dl.RESULTS_DIR, "part1_summary.json"), "w") as fh:
        json.dump(
            dict(
                total_cost=result["total_cost"],
                cost_breakdown=result["cost_breakdown"],
                feu_led_total=result["feu_led_total"],
                feu_soft_total=result["feu_soft_total"],
                feu_total=result["feu_total"],
                ports_open=result["ports_open"],
                depots_open=result["depots_open"],
                setup=result["setup"],
            ),
            fh, indent=2,
        )

    # soft flows depot -> stadium
    with open(os.path.join(dl.RESULTS_DIR, "part1_flows_soft.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["depot_node", "stadium_node", "volume_m3"])
        for (d, s), v in sorted(result["flows_soft_ds"].items()):
            w.writerow([d, s, round(v, 3)])

    # led flows port -> stadium
    with open(os.path.join(dl.RESULTS_DIR, "part1_flows_led.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["port_node", "stadium_node", "volume_m3"])
        for (p, s), v in sorted(result["flows_led_ps"].items()):
            w.writerow([p, s, round(v, 3)])


def run_comparison() -> list:
    """Alternative set-ups for the managerial comparison (guideline p.6)."""
    setups = [
        ("baseline (LED direct, depots, weight, LCL)",
         dict(led_direct=True, use_depots=True, enforce_weight=True, allow_lcl=True)),
        ("LED via depot (no direct)",
         dict(led_direct=False, use_depots=True, enforce_weight=True, allow_lcl=True)),
        ("volume-only (no weight constraint)",
         dict(led_direct=True, use_depots=True, enforce_weight=False, allow_lcl=True)),
        ("FCL-only (no LCL)",
         dict(led_direct=True, use_depots=True, enforce_weight=True, allow_lcl=False)),
    ]
    rows = []
    for label, kw in setups:
        r = solve_lrp(verbose=False, **kw)
        if r["status"] != "OPTIMAL":
            rows.append((label, None, None, None, None))
            continue
        rows.append((label, r["total_cost"], r["feu_led_total"],
                     r["feu_soft_total"], r["feu_total"]))
    return rows


def export_comparison(rows: list) -> None:
    path = os.path.join(dl.RESULTS_DIR, "part1_setup_comparison.csv")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["setup", "total_cost_usd", "feu_led", "feu_soft", "feu_total"])
        for label, cost, fl, fs, ft in rows:
            w.writerow([label,
                        f"{cost:.0f}" if cost is not None else "INFEASIBLE",
                        f"{fl:.0f}" if fl is not None else "",
                        f"{fs:.0f}" if fs is not None else "",
                        f"{ft:.0f}" if ft is not None else ""])


def main() -> None:
    print(">>> Solving baseline LRP ...")
    baseline = solve_lrp(verbose=True)
    export_baseline(baseline)

    print("\n>>> Running set-up comparison ...")
    rows = run_comparison()
    export_comparison(rows)
    print(f"\n{'Set-up':45} {'Cost':>12} {'FEU(L/S/T)':>14}")
    for label, cost, fl, fs, ft in rows:
        if cost is None:
            print(f"{label:45} {'INFEASIBLE':>12}")
        else:
            print(f"{label:45} ${cost:>11,.0f} {fl:.0f}/{fs:.0f}/{ft:.0f}")
    print(f"\nResults written to {dl.RESULTS_DIR}")


if __name__ == "__main__":
    main()
