"""
Visualisations (guideline p.3/p.6: "give graphical representations").

Produces, in outputs/figures/:
  * part1_network_map.png    -- geographic map: China->ports->depots->stadiums
  * part1_cost_breakdown.png -- stacked bar of the Part I cost components
  * part1_feu_by_class.png   -- LED vs SOFT FEU, weight-on vs weight-off
  * part2_stage_split.png    -- anticipatory (stage-1) vs reactive (stage-2)
  * part2_feasibility.png    -- per-match window vs min transit (forced-anticip)

Uses matplotlib only (no internet, no basemap) -- coastlines are approximated
by plotting node lat/lon directly, which is enough to read the network.
"""
from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl  # noqa: E402
from part1_lrp.model import solve_lrp  # noqa: E402
from part2_stochastic.model import solve_stochastic  # noqa: E402

import csv  # noqa: E402


def _node_coords():
    rows = []
    with open(os.path.join(dl.RAW_DIR, "nodes.csv"), encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    return {r["node_id"]: (float(r["latitude"]), float(r["longitude"]),
                           r["node_type"], r["node_name"]) for r in rows}


def fig_network_map():
    coords = _node_coords()
    r = solve_lrp(verbose=False)
    fig, ax = plt.subplots(figsize=(11, 7))

    # plot all nodes faintly
    styles = {"stadium": ("o", "#1f77b4", 40), "candidate_depot": ("s", "#ff7f0e", 90),
              "port_gateway": ("^", "#2ca02c", 120), "production_site": ("D", "#888", 30)}
    for nid, (lat, lon, ntype, name) in coords.items():
        if ntype in styles and "CHINA" not in nid:
            m, c, s = styles[ntype]
            faint = 0.25 if ntype == "production_site" else 1.0
            ax.scatter(lon, lat, marker=m, c=c, s=s, alpha=faint, zorder=3,
                       edgecolors="k", linewidths=0.3)

    # soft flows depot->stadium (grey)
    for (d, s), v in r["flows_soft_ds"].items():
        if d in coords and s in coords:
            ax.plot([coords[d][1], coords[s][1]], [coords[d][0], coords[s][0]],
                    color="#999", lw=0.6 + 2.0 * v / 120, alpha=0.5, zorder=2)
    # led flows port->stadium (green dashed)
    for (p, s), v in r["flows_led_ps"].items():
        if p in coords and s in coords:
            ax.plot([coords[p][1], coords[s][1]], [coords[p][0], coords[s][0]],
                    color="#2ca02c", lw=0.6 + 2.0 * v / 67, alpha=0.4,
                    ls="--", zorder=1)

    # highlight open ports/depots
    for p in r["ports_open"]:
        lat, lon = coords[p][0], coords[p][1]
        ax.scatter(lon, lat, marker="^", c="#2ca02c", s=260, edgecolors="k",
                   linewidths=1.2, zorder=5)
    for d in r["depots_open"]:
        lat, lon = coords[d][0], coords[d][1]
        ax.scatter(lon, lat, marker="s", c="#ff7f0e", s=200, edgecolors="k",
                   linewidths=1.2, zorder=5)

    ax.set_title(f"Part I optimal network -- ${r['total_cost']:,.0f}  "
                 f"({r['feu_total']:.0f} FEU)\n"
                 "green^ = open port (LED direct, dashed), orange# = open depot "
                 "(soft, grey), blue o = stadium")
    ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
    ax.grid(alpha=0.2)
    _save(fig, "part1_network_map.png")


def fig_cost_breakdown():
    r = solve_lrp(verbose=False)
    cb = r["cost_breakdown"]
    labels = list(cb.keys())
    vals = [cb[k] for k in labels]
    fig, ax = plt.subplots(figsize=(9, 5))
    bottom = 0
    colors = plt.cm.tab10.colors
    for i, (lab, v) in enumerate(zip(labels, vals)):
        ax.bar("Part I", v, bottom=bottom, label=f"{lab} (${v:,.0f})",
               color=colors[i % 10])
        bottom += v
    ax.set_ylabel("USD")
    ax.set_title(f"Part I cost breakdown -- total ${r['total_cost']:,.0f}")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=8)
    _save(fig, "part1_cost_breakdown.png")


def fig_feu_by_class():
    on = solve_lrp(enforce_weight=True, verbose=False)
    off = solve_lrp(enforce_weight=False, verbose=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    cases = ["weight ON\n(realistic)", "weight OFF\n(volume only)"]
    led = [on["feu_led_total"], off["feu_led_total"]]
    soft = [on["feu_soft_total"], off["feu_soft_total"]]
    ax.bar(cases, led, label="LED FEU", color="#d62728")
    ax.bar(cases, soft, bottom=led, label="SOFT FEU", color="#1f77b4")
    for i, (l, s) in enumerate(zip(led, soft)):
        ax.text(i, l + s + 1, f"{l+s:.0f} FEU", ha="center", fontweight="bold")
    ax.set_ylabel("Number of 40ft containers (FEU)")
    ax.set_title("The LED weight effect: 26t ceiling forces more containers\n"
                 f"${on['total_cost']:,.0f} vs ${off['total_cost']:,.0f}")
    ax.legend()
    _save(fig, "part1_feu_by_class.png")


def fig_part2_stage_split():
    r = solve_stochastic(verbose=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar("Expected cost", r["stage1_cost"], label=f"Stage-1 anticipatory "
           f"(${r['stage1_cost']:,.0f})", color="#9467bd")
    ax.bar("Expected cost", r["stage2_expected_cost"], bottom=r["stage1_cost"],
           label=f"Stage-2 reactive (${r['stage2_expected_cost']:,.0f})",
           color="#17becf")
    ax.set_ylabel("USD")
    ax.set_title(f"Part II two-stage cost split -- total ${r['total_expected_cost']:,.0f}\n"
                 f"{r['n_forced']} of 16 matches FORCED anticipatory (window too short)")
    ax.legend()
    _save(fig, "part2_stage_split.png")


def fig_part2_feasibility():
    from datetime import date
    road = dl.load_road_edges()
    prod = dl.load_production_sites()
    sites = [n for n in prod if n != "PROD_CHINA_SHANGHAI"]
    GSE = date(2026, 6, 27)
    # use scenario 0 venues/dates
    rows = []
    with open(os.path.join(dl.GENERATED_DIR, "part2_scenarios.csv"), encoding="utf-8") as fh:
        for rr in csv.DictReader(fh):
            if rr["scenario"] == "0":
                rows.append(rr)
    matches, windows, mintransit = [], [], []
    for rr in rows:
        venue = rr["venue_node"]
        y, m, d = map(int, rr["date"].split("-"))
        win = (date(y, m, d) - GSE).days
        ts = [road[(j, venue)]["transit_time_days"] for j in sites
              if (j, venue) in road and road[(j, venue)]["transit_time_days"] is not None]
        matches.append(int(rr["match"])); windows.append(win)
        mintransit.append(min(ts) if ts else None)
    fig, ax = plt.subplots(figsize=(11, 5))
    x = range(len(matches))
    ax.bar([i - 0.2 for i in x], windows, width=0.4, label="window (days)",
           color="#2ca02c")
    ax.bar([i + 0.2 for i in x], mintransit, width=0.4,
           label="min transit (days, best site)", color="#d62728")
    ax.axhline(1, color="k", ls=":", lw=1, label="production = 1 day")
    ax.set_xticks(list(x)); ax.set_xticklabels(matches, rotation=0, fontsize=7)
    ax.set_xlabel("R32 match"); ax.set_ylabel("days")
    ax.set_title("Part II feasibility: reactive needs min_transit <= window - 1\n"
                 "matches where red+1 > green must be served anticipatorily")
    ax.legend()
    _save(fig, "part2_feasibility.png")


def _save(fig, name):
    os.makedirs(dl.FIGURES_DIR, exist_ok=True)
    path = os.path.join(dl.FIGURES_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


def main():
    fig_network_map()
    fig_cost_breakdown()
    fig_feu_by_class()
    fig_part2_stage_split()
    fig_part2_feasibility()


if __name__ == "__main__":
    main()
