"""
Export derived result tables for report insertion.

Writes CSV files to outputs/results/:
  * part1_port_utilization.csv       per-port FEU breakdown + LCL
  * part1_cost_allocation.csv        cost components + % of total
  * part2_anticipatory_detail.csv    per R32 match: forced/reactive + window
  * executive_summary.csv            one-stop KPI table (Part I + Part II)
  * part2_reactive_site_usage.csv    production site usage across 50 scenarios
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


def export_anticipatory_detail(r: dict | None = None):
    """Table 3: per R32 match: forced/reactive, window, venue."""
    if r is None:
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


def export_executive_summary(r2: dict | None = None):
    """Table 4: one-stop KPI table consolidating Part I + Part II headline numbers."""
    path = os.path.join(dl.RESULTS_DIR, "part1_summary.json")
    with open(path, encoding="utf-8") as fh:
        s1 = json.load(fh)

    if r2 is None:
        r2 = solve_stochastic(verbose=False)

    # Read part1 setup comparison to compute weight savings
    setup_csv = os.path.join(dl.RESULTS_DIR, "part1_setup_comparison.csv")
    setup_rows = []
    if os.path.exists(setup_csv):
        with open(setup_csv, newline="", encoding="utf-8") as fh:
            setup_rows = list(csv.DictReader(fh))
    weight_savings = ""
    for sr in setup_rows:
        if "Volume-only" in sr["setup"]:
            weight_savings = round(float(sr["total_cost_usd"]) - s1["total_cost"], 0)
            break

    # Read part2 sensitivity to compute production-cost slope
    sens_csv = os.path.join(dl.RESULTS_DIR, "part2_sensitivity.csv")
    slope = ""
    if os.path.exists(sens_csv):
        with open(sens_csv, newline="", encoding="utf-8") as fh:
            sens_rows = [r for r in csv.DictReader(fh) if r["parameter"] == "production_cost_per_m2"]
        if len(sens_rows) >= 2:
            sens_rows.sort(key=lambda r: float(r["value"].replace("$", "")))
            x_lo = float(sens_rows[0]["value"].replace("$", ""))
            x_hi = float(sens_rows[-1]["value"].replace("$", ""))
            c_lo = float(sens_rows[0]["total_expected_cost_usd"])
            c_hi = float(sens_rows[-1]["total_expected_cost_usd"])
            slope = round((c_hi - c_lo) / (x_hi - x_lo), 0)

    rows = [
        {"part": "Part I",  "metric": "Total cost",                       "value": round(s1["total_cost"], 0),       "unit": "USD"},
        {"part": "Part I",  "metric": "Total FEU containers",             "value": int(s1["feu_total"]),              "unit": "FEU"},
        {"part": "Part I",  "metric": "LED FEU containers",               "value": int(s1["feu_led_total"]),          "unit": "FEU"},
        {"part": "Part I",  "metric": "Soft-goods FEU containers",        "value": int(s1["feu_soft_total"]),         "unit": "FEU"},
        {"part": "Part I",  "metric": "Ports opened",                     "value": len(s1["ports_open"]),             "unit": f"({'/'.join(p.replace('PORT_', '').replace('_LB', '') for p in s1['ports_open'])})"},
        {"part": "Part I",  "metric": "Depots opened",                    "value": len(s1["depots_open"]),            "unit": f"({'/'.join(d.replace('_DEPOT_NODE', '') for d in s1['depots_open'])})"},
        {"part": "Part I",  "metric": "Ocean-freight share of total",     "value": round(100 * s1["cost_breakdown"]["sea"] / s1["total_cost"], 1), "unit": "%"},
        {"part": "Part I",  "metric": "Weight-constraint cost impact",    "value": weight_savings,                    "unit": "USD vs volume-only baseline"},
        {"part": "Part II", "metric": "Total expected cost",              "value": round(r2["total_expected_cost"], 0), "unit": "USD"},
        {"part": "Part II", "metric": "Stage-1 anticipatory cost",        "value": round(r2["stage1_cost"], 0),       "unit": "USD"},
        {"part": "Part II", "metric": "Stage-2 expected reactive cost",   "value": round(r2["stage2_expected_cost"], 0), "unit": "USD"},
        {"part": "Part II", "metric": "Forced-anticipatory matches",      "value": r2["n_forced"],                    "unit": "of 16 R32 matches"},
        {"part": "Part II", "metric": "Scenarios analysed",               "value": r2["n_scenarios"],                 "unit": "Monte-Carlo scenarios"},
        {"part": "Part II", "metric": "Production-cost cost slope",       "value": slope,                             "unit": "USD per +$1 / m²"},
    ]

    out = os.path.join(dl.RESULTS_DIR, "executive_summary.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["part", "metric", "value", "unit"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out}")


def export_reactive_site_usage(r2: dict | None = None):
    """Table 5: reactive production-site usage frequency across 50 scenarios."""
    if r2 is None:
        r2 = solve_stochastic(verbose=False)
    usage = r2.get("site_usage_freq", {})

    region_map = {
        "PROD_WASS_NC":      "USA — North Carolina",
        "PROD_WASS_TEMPE":   "USA — Arizona",
        "PROD_TLC_TUKWILA":  "USA — Washington",
        "PROD_TLC_BARRIE":   "Canada — Ontario",
        "PROD_TLC_TAMPA":    "USA — Florida",
        "PROD_CHINA_SHANGHAI": "China",
    }

    rows = []
    for site, freq in sorted(usage.items(), key=lambda kv: kv[1], reverse=True):
        rows.append({
            "production_site":            site,
            "region":                     region_map.get(site, "—"),
            "avg_matches_per_scenario":   round(freq, 3),
            "frequency_pct":              round(freq * 100, 1),
        })

    if not rows:
        rows = [{"production_site": "—", "region": "—",
                 "avg_matches_per_scenario": 0, "frequency_pct": 0}]

    out = os.path.join(dl.RESULTS_DIR, "part2_reactive_site_usage.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {out}")


def main():
    os.makedirs(dl.RESULTS_DIR, exist_ok=True)
    # Solve Part II once and reuse across functions
    r2 = solve_stochastic(verbose=False)

    export_port_utilization()
    export_cost_allocation()
    export_anticipatory_detail(r2)
    export_executive_summary(r2)
    export_reactive_site_usage(r2)
    print("All result tables exported.")


if __name__ == "__main__":
    main()
