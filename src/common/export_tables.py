"""
Export derived result tables for report insertion.

Writes three CSV files to outputs/results/:
  * part1_port_utilization.csv   -- per-port FEU breakdown + LCL
  * part1_cost_allocation.csv    -- cost components + % of total
  * part2_anticipatory_detail.csv -- per R32 match: forced/reactive + window
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl  # noqa: E402
from part2_stochastic.model import solve_stochastic  # noqa: E402


def export_port_utilization():
    """Table 1: per-port FEU + LCL breakdown."""
    path = os.path.join(dl.RESULTS_DIR, "part1_summary.json")
    with open(path, encoding="utf-8") as fh:
        s = json.load(fh)

    total_feu = s["feu_total"]
    rows = []
    for port, v in s["ports_open"].items():
        feu_led = v["feu_led"]
        feu_soft = v["feu_soft"]
        feu_total = feu_led + feu_soft
        lcl = v["lcl_soft"]
        pct = 100.0 * feu_total / total_feu if total_feu > 0 else 0.0
        # friendly short name
        short = port.replace("PORT_", "").replace("_LB", "")
        rows.append({
            "port": short,
            "port_node": port,
            "feu_led": int(feu_led),
            "feu_soft": int(feu_soft),
            "feu_total": int(feu_total),
            "lcl_m3": round(lcl, 2),
            "pct_feu_of_total": round(pct, 1),
        })

    out = os.path.join(dl.RESULTS_DIR, "part1_port_utilization.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out}")


def export_cost_allocation():
    """Table 2: cost components + % of total."""
    path = os.path.join(dl.RESULTS_DIR, "part1_summary.json")
    with open(path, encoding="utf-8") as fh:
        s = json.load(fh)

    total = s["total_cost"]
    rows = []
    labels = {
        "sea":                   "Ocean freight (sea)",
        "depot_fixed":           "Depot fixed cost",
        "depot_handling":        "Depot handling",
        "truck_port_depot":      "Trucking port → depot",
        "truck_depot_stadium":   "Trucking depot → stadium",
        "truck_port_stadium_led": "Trucking port → stadium (LED direct)",
    }
    for key, label in labels.items():
        v = s["cost_breakdown"][key]
        rows.append({
            "component": label,
            "cost_usd": round(v, 2),
            "pct_of_total": round(100.0 * v / total, 1),
        })
    # total row
    rows.append({
        "component": "TOTAL",
        "cost_usd": round(total, 2),
        "pct_of_total": 100.0,
    })

    out = os.path.join(dl.RESULTS_DIR, "part1_cost_allocation.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["component", "cost_usd", "pct_of_total"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out}")


def export_anticipatory_detail():
    """Table 3: per R32 match: forced/reactive, window, venue."""
    r = solve_stochastic(verbose=False)

    rows = []
    for mid in sorted(r["match_venue"].keys()):
        venue = r["match_venue"][mid]
        window = r["match_window"].get(mid, None)
        is_forced = mid in r["forced_anticipatory_matches"]
        vol = r["anticipatory_by_match"].get(mid, 0.0)
        rows.append({
            "match_id": mid,
            "venue_node": venue,
            "window_days": window,
            "is_forced": is_forced,
            "stage1_volume_m3": round(vol, 4),
            "decision": "anticipatory" if is_forced else "reactive",
        })

    out = os.path.join(dl.RESULTS_DIR, "part2_anticipatory_detail.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out}")


def main():
    os.makedirs(dl.RESULTS_DIR, exist_ok=True)
    export_port_utilization()
    export_cost_allocation()
    export_anticipatory_detail()
    print("All result tables exported.")


if __name__ == "__main__":
    main()
