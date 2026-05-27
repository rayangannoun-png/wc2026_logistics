"""
Visualisations — FIFA WC2026 Logistics (MGT-530, HEC Lausanne / EPFL E4S).

Colour palette: official FIFA WC2026 brand colours.
All figures are saved as PNG (130 dpi) into outputs/figures/.

Figures produced (25 total):

  --- Part I analytical (deterministic LRP) ---
    part1_network_map.png
    part1_cost_breakdown.png
    part1_feu_by_class.png
    part1_port_utilization.png
    part1_stadium_demand.png
    part1_demand_heatmap.png
    part1_setup_comparison.png
    part1_sensitivity_tornado.png
    part1_flow_matrix.png
    part1_cost_donut.png
    part1_feu_efficiency.png              (NEW)

  --- Part I conceptual diagrams ---
    part1_network_architecture.png        (NEW)
    part1_feu_constraint_box.png          (NEW)

  --- Part II analytical (two-stage stochastic) ---
    part2_stage_split.png
    part2_feasibility.png
    part2_sensitivity_tornado.png
    part2_stage_by_param.png
    part2_prod_cost_curve.png
    part2_anticipatory_by_match.png
    part2_waste_curve.png                 (NEW)
    part2_production_days.png             (NEW)
    part2_reactive_sites.png              (NEW)
    part2_forced_map.png                  (NEW)
    part2_sensitivity_grid.png            (NEW)

  --- Part II conceptual diagrams ---
    part2_two_stage_timeline.png          (NEW)
"""
from __future__ import annotations

import csv
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from matplotlib.lines import Line2D
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl
from part1_lrp.model import solve_lrp
from part2_stochastic.model import solve_stochastic


# ============================================================================
# === STYLE === FIFA WC2026 brand palette
# ============================================================================
F_PURPLE  = "#622EEA"
F_RED     = "#D31E03"
F_LIME    = "#AEEA00"
F_BLUE    = "#375AFE"
F_LBLUE   = "#8DBAFE"
F_NAVY    = "#1A2688"

# Semantic aliases
C_LED       = F_BLUE
C_SOFT      = F_LBLUE
C_STAGE1    = F_PURPLE
C_STAGE2    = F_LBLUE
C_FORCED    = F_RED
C_REACTIVE  = F_LIME
C_SAVINGS   = F_LIME
C_EXTRA     = F_RED
C_BASELINE  = F_NAVY
C_SEA       = F_NAVY
C_NEUTRAL   = "#C8D0E0"

COST_COLORS = [F_NAVY, F_PURPLE, F_BLUE, F_LBLUE, F_RED, F_LIME]

plt.rcParams.update({
    "font.family":            "DejaVu Sans",
    "font.size":              10,
    "axes.facecolor":         "#FAFBFE",
    "figure.facecolor":       "white",
    "axes.edgecolor":         F_NAVY,
    "axes.labelcolor":        F_NAVY,
    "axes.labelsize":         11,
    "axes.titlesize":         13,
    "axes.titleweight":       "bold",
    "axes.titlepad":          10,
    "axes.spines.top":        False,
    "axes.spines.right":      False,
    "axes.grid":              True,
    "grid.color":             "#DADCE8",
    "grid.linestyle":         "--",
    "grid.linewidth":         0.6,
    "grid.alpha":             0.7,
    "xtick.color":            F_NAVY,
    "ytick.color":            F_NAVY,
    "xtick.labelsize":        9,
    "ytick.labelsize":        9,
    "legend.fontsize":        9,
    "legend.framealpha":      0.92,
    "legend.edgecolor":       C_NEUTRAL,
    "text.color":             F_NAVY,
    "figure.dpi":             130,
})


# ============================================================================
# Helpers
# ============================================================================

def _node_coords() -> dict:
    with open(os.path.join(dl.RAW_DIR, "nodes.csv"), encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    return {r["node_id"]: (float(r["latitude"]), float(r["longitude"]),
                           r["node_type"], r["node_name"]) for r in rows}


def _load_json(name: str) -> dict:
    with open(os.path.join(dl.RESULTS_DIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def _read_results_csv(name: str) -> list[dict]:
    with open(os.path.join(dl.RESULTS_DIR, name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _save(fig, name: str):
    os.makedirs(dl.FIGURES_DIR, exist_ok=True)
    path = os.path.join(dl.FIGURES_DIR, name)
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {path}")


def _clean_ax(ax, grid_axis: str = "y"):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C_NEUTRAL)
    ax.spines["bottom"].set_color(C_NEUTRAL)
    ax.grid(True, axis=grid_axis)
    ax.grid(False, axis="x" if grid_axis == "y" else "y")


def _title_block(ax, title: str, subtitle: str = ""):
    full = title if not subtitle else f"{title}\n{subtitle}"
    ax.set_title(full, color=F_NAVY, fontsize=13, fontweight="bold", pad=10)


def _footer(fig, source: str):
    """Add a small data-source footnote at bottom-right of the figure."""
    fig.text(0.995, 0.005,
             f"Source: {source}  ·  MGT-530 / WC2026 logistics",
             fontsize=7, color="#9098B0", style="italic",
             ha="right", va="bottom")


def _fifa_cmap(light="#EEF1FB", dark=F_NAVY):
    return mcolors.LinearSegmentedColormap.from_list("fifa", [light, dark])


def _coastline_polygon():
    """
    Approximate North-American coastline drawn as a single polyline (no map lib).
    Returns a list of (lon, lat) pairs to plot as background context.
    """
    return [
        # West coast US (north to south)
        (-123.5, 49.3), (-124.0, 47.5), (-124.0, 44.0), (-124.0, 40.5),
        (-122.5, 37.5), (-120.5, 34.5), (-117.5, 32.7),
        # Mexico West coast
        (-115.0, 30.5), (-110.0, 24.5), (-106.0, 21.5), (-105.0, 20.0),
        (-100.0, 17.0), (-96.0, 15.7), (-92.0, 14.7),
        # Mexico South / Gulf
        (-89.0, 16.0), (-87.5, 18.5), (-91.0, 19.0), (-94.5, 18.5),
        (-97.5, 21.0), (-97.0, 25.5),
        # Gulf US
        (-94.0, 29.5), (-90.0, 29.0), (-87.0, 30.5), (-82.0, 27.0),
        # Florida tip
        (-80.0, 25.5), (-80.0, 27.5), (-80.5, 31.5),
        # East coast
        (-76.0, 34.5), (-74.5, 39.0), (-71.5, 41.5), (-70.0, 42.5),
        (-67.0, 44.5), (-65.0, 45.5),
        # Canada East
        (-61.0, 46.0), (-65.0, 48.5), (-69.0, 48.0),
        # Great Lakes proxy / North border
        (-80.0, 43.5), (-83.0, 42.0), (-87.0, 41.7),
        (-90.0, 43.2), (-95.0, 45.5), (-100.0, 49.0), (-115.0, 49.0),
        (-123.5, 49.3),
    ]


def _draw_coastline(ax, fill=True):
    pts = _coastline_polygon()
    lons = [p[0] for p in pts]
    lats = [p[1] for p in pts]
    if fill:
        ax.fill(lons, lats, color="#EAF0FB", alpha=0.7, zorder=0,
                edgecolor="#C8D0E0", linewidth=0.8)
    else:
        ax.plot(lons, lats, color="#C8D0E0", lw=0.8, zorder=0)


# ============================================================================
# === Part I analytical ===
# ============================================================================

def fig_network_map():
    coords = _node_coords()
    r      = solve_lrp(verbose=False)

    fig, ax = plt.subplots(figsize=(12, 7), facecolor="white")
    _draw_coastline(ax, fill=True)

    style_map = {
        "stadium":         ("o", C_LED,     45, 0.85),
        "candidate_depot": ("s", F_PURPLE, 100, 0.30),
        "port_gateway":    ("^", F_LIME,   140, 0.30),
        "production_site": ("D", C_NEUTRAL, 28, 0.45),
    }
    for nid, (lat, lon, ntype, _) in coords.items():
        if ntype in style_map and "CHINA" not in nid:
            m, c, s, a = style_map[ntype]
            ax.scatter(lon, lat, marker=m, color=c, s=s, alpha=a,
                       edgecolors="white", linewidths=0.5, zorder=3)

    for (d, sv), v in r["flows_soft_ds"].items():
        if d in coords and sv in coords:
            ax.plot([coords[d][1], coords[sv][1]],
                    [coords[d][0], coords[sv][0]],
                    color=C_SOFT, lw=0.6 + 2.5 * v / 130,
                    alpha=0.60, zorder=2)
    for (p, sv), v in r["flows_led_ps"].items():
        if p in coords and sv in coords:
            ax.plot([coords[p][1], coords[sv][1]],
                    [coords[p][0], coords[sv][0]],
                    color=F_LIME, lw=1.3, alpha=0.55, ls="--", zorder=1)

    # offset port marker if colocated with depot (LA case)
    port_offset = {"PORT_LA_LB": (0.0, -0.9)}
    for p in r["ports_open"]:
        lat, lon = coords[p][0], coords[p][1]
        dy, dx = port_offset.get(p, (0.0, 0.0))
        ax.scatter(lon + dx, lat + dy, marker="^", color=F_LIME, s=340,
                   edgecolors=F_NAVY, linewidths=1.6, zorder=7)
        ax.annotate(coords[p][3] if len(coords[p][3]) < 14 else p.replace("PORT_", ""),
                    (lon + dx, lat + dy),
                    xytext=(7, -3), textcoords="offset points",
                    fontsize=8, color=F_NAVY, fontweight="bold", zorder=8)
    for d in r["depots_open"]:
        lat, lon = coords[d][0], coords[d][1]
        ax.scatter(lon, lat, marker="s", color=F_PURPLE, s=240,
                   edgecolors=F_NAVY, linewidths=1.5, zorder=6)
        ax.annotate(d.replace("_DEPOT_NODE", ""),
                    (lon, lat), xytext=(7, 8), textcoords="offset points",
                    fontsize=8, color=F_NAVY, fontweight="bold", zorder=8)

    for nid, (lat, lon, ntype, name) in coords.items():
        if ntype == "stadium":
            ax.scatter(lon, lat, marker="o", color=C_LED, s=60,
                       edgecolors="white", linewidths=0.8, zorder=5)

    legend_els = [
        Line2D([0], [0], marker="^", color="w", markerfacecolor=F_LIME,
               markersize=13, markeredgecolor=F_NAVY, label="Open port (LED direct, dashed)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor=F_PURPLE,
               markersize=11, markeredgecolor=F_NAVY, label="Open depot (soft, solid)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=C_LED,
               markersize=9, markeredgecolor="white", label="Stadium"),
        Line2D([0], [0], color=C_SOFT, lw=2.5, label="Soft-goods flow"),
        Line2D([0], [0], color=F_LIME, lw=2.5, ls="--", label="LED direct flow"),
    ]
    ax.legend(handles=legend_els, loc="lower left", fontsize=8.5,
              framealpha=0.95, edgecolor=C_NEUTRAL)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(-128, -60)
    ax.set_ylim(14, 51)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _title_block(ax,
                 "Part I — Optimal supply network",
                 f"Total ${r['total_cost']:,.0f}  ·  {r['feu_total']:.0f} FEU  ·  "
                 f"{len(r['ports_open'])} ports  ·  {len(r['depots_open'])} depots")
    fig.tight_layout()
    _footer(fig, "solve_lrp() + nodes.csv")
    _save(fig, "part1_network_map.png")


def fig_cost_breakdown():
    r   = solve_lrp(verbose=False)
    cb  = r["cost_breakdown"]
    keys = list(cb.keys())
    vals = [cb[k] for k in keys]
    friendly = {
        "sea":                    "Ocean freight",
        "depot_fixed":            "Depot fixed",
        "depot_handling":         "Depot handling",
        "truck_port_depot":       "Truck port→depot",
        "truck_depot_stadium":    "Truck depot→stadium",
        "truck_port_stadium_led": "Truck port→stadium (LED)",
    }

    fig, ax = plt.subplots(figsize=(9, 6))
    bottom = 0
    for k, v, c in zip(keys, vals, COST_COLORS):
        ax.bar("Part I", v, bottom=bottom,
               label=f"{friendly[k]}  (${v:,.0f})",
               color=c, edgecolor="white")
        if v > r["total_cost"] * 0.04:
            pct = 100 * v / r["total_cost"]
            ax.text(0, bottom + v / 2, f"{pct:.1f}%",
                    ha="center", va="center", fontsize=9,
                    color="white" if c in (F_NAVY, F_PURPLE, F_BLUE) else F_NAVY,
                    fontweight="bold")
        bottom += v

    ax.set_ylabel("USD")
    ax.set_ylim(0, r["total_cost"] * 1.1)
    ax.set_xticks([])
    _clean_ax(ax, "y")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left")
    _title_block(ax,
                 "Part I — Cost breakdown by component",
                 f"Ocean freight is the dominant cost driver (~68 % of ${r['total_cost']:,.0f})")
    fig.tight_layout()
    _footer(fig, "part1_summary.json")
    _save(fig, "part1_cost_breakdown.png")


def fig_feu_by_class():
    on  = solve_lrp(enforce_weight=True,  verbose=False)
    off = solve_lrp(enforce_weight=False, verbose=False)

    cases = ["Weight constraint ON\n(realistic, 26 t/FEU)",
             "Weight constraint OFF\n(volume-only, 67 m³/FEU)"]
    led  = [on["feu_led_total"],  off["feu_led_total"]]
    soft = [on["feu_soft_total"], off["feu_soft_total"]]

    fig, ax = plt.subplots(figsize=(8, 5.5))
    x = np.arange(len(cases))
    w = 0.5
    ax.bar(x, led,  w, label="LED FEU",  color=C_LED,  edgecolor="white")
    ax.bar(x, soft, w, bottom=led, label="Soft FEU", color=C_SOFT, edgecolor="white")

    for i, (l, s) in enumerate(zip(led, soft)):
        ax.text(i, l + s + 1.2, f"{int(l+s)} FEU",
                ha="center", fontsize=12, fontweight="bold", color=F_NAVY)
        ax.text(i, l / 2, f"{int(l)}",
                ha="center", va="center", fontsize=10, color="white", fontweight="bold")
        ax.text(i, l + s / 2, f"{int(s)}",
                ha="center", va="center", fontsize=10, color=F_NAVY, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(cases, fontsize=10)
    ax.set_ylabel("Number of 40 ft containers (FEU)")
    _clean_ax(ax, "y")
    ax.legend(loc="upper right")
    _title_block(ax,
                 "The LED weight effect: 26 t ceiling forces more containers",
                 f"${on['total_cost']:,.0f}  vs  ${off['total_cost']:,.0f}  "
                 f"(+${on['total_cost']-off['total_cost']:,.0f} / "
                 f"+{on['feu_total']-off['feu_total']:.0f} FEU)")
    fig.tight_layout()
    _footer(fig, "solve_lrp() weight ON/OFF")
    _save(fig, "part1_feu_by_class.png")


def fig_port_utilization():
    s = _load_json("part1_summary.json")
    pd = s["ports_open"]

    short = {"PORT_LA_LB": "LA / Long Beach", "PORT_NY_NJ": "New York / NJ", "PORT_VAN": "Vancouver"}
    port_order = list(pd.keys())
    labels   = [short.get(p, p) for p in port_order]
    feu_led  = [pd[p]["feu_led"]  for p in port_order]
    feu_soft = [pd[p]["feu_soft"] for p in port_order]
    lcl_vals = [pd[p]["lcl_soft"] for p in port_order]

    x = np.arange(len(labels))
    w = 0.32
    fig, ax = plt.subplots(figsize=(9, 5.2))

    b_led  = ax.bar(x - w / 2, feu_led,  w, label="LED FEU",  color=C_LED,  edgecolor="white")
    b_soft = ax.bar(x + w / 2, feu_soft, w, label="Soft FEU", color=C_SOFT, edgecolor="white")

    for bars in (b_led, b_soft):
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.25,
                        f"{int(h)}", ha="center", va="bottom",
                        fontsize=10, fontweight="bold", color=F_NAVY)

    for i, lcl in enumerate(lcl_vals):
        if lcl > 0:
            ax.text(x[i], -2.2, f"+ {lcl:.1f} m³ LCL",
                    ha="center", fontsize=8, color=F_PURPLE, style="italic")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("FEU (40 ft containers)")
    ax.set_ylim(bottom=-3.5)
    _clean_ax(ax, "y")
    ax.legend(loc="upper right")
    _title_block(ax,
                 "Part I — Port utilisation by material class",
                 f"LA handles overflow as LCL  ·  Vancouver specialises in LED only")
    fig.tight_layout()
    _footer(fig, "part1_summary.json → ports_open")
    _save(fig, "part1_port_utilization.png")


def fig_stadium_demand():
    path = os.path.join(dl.GENERATED_DIR, "stadium_demand_by_class.csv")
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    rows.sort(key=lambda r: float(r["vol_total_m3"]), reverse=True)
    stads  = [r["stadium_id"] for r in rows]
    v_led  = [float(r["vol_led_m3"])  for r in rows]
    v_soft = [float(r["vol_soft_m3"]) for r in rows]
    v_tot  = [float(r["vol_total_m3"]) for r in rows]

    fig, ax = plt.subplots(figsize=(11, 7))
    y = np.arange(len(stads))
    h = 0.62

    ax.barh(y, v_led,  h, label="LED perimeter (constant 67 m³)",
            color=C_LED,  edgecolor="white", linewidth=0.4)
    ax.barh(y, v_soft, h, left=v_led, label="Soft goods (variable by stadium)",
            color=C_SOFT, edgecolor="white", linewidth=0.4)

    for i, (tot, vl) in enumerate(zip(v_tot, v_led)):
        ax.text(tot + 1.5, i, f"{tot:.0f} m³",
                va="center", fontsize=8.5, color=F_NAVY, fontweight="bold")
        ax.text(vl / 2, i, "LED", va="center", ha="center",
                fontsize=7, color="white", fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(stads, fontsize=9)
    ax.set_xlabel("Volume (m³)")
    ax.set_xlim(0, max(v_tot) * 1.15)
    _clean_ax(ax, "x")
    ax.legend(loc="lower right")
    _title_block(ax,
                 "Part I — Stadium demand by material class",
                 f"Demand varies from {min(v_tot):.0f} m³ (TOR) to {max(v_tot):.0f} m³ (DAL)")
    fig.tight_layout()
    _footer(fig, "stadium_demand_by_class.csv")
    _save(fig, "part1_stadium_demand.png")


def fig_demand_by_poste():
    path = os.path.join(dl.GENERATED_DIR, "stadium_demand_by_poste.csv")
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    stads  = sorted({r["stadium_id"] for r in rows})
    postes = sorted({r["poste"] for r in rows})

    poste_totals = {p: sum(float(r["volume_m3"]) for r in rows if r["poste"] == p) for p in postes}
    postes = sorted(postes, key=lambda p: poste_totals[p], reverse=True)
    stad_totals = {s: sum(float(r["volume_m3"]) for r in rows if r["stadium_id"] == s) for s in stads}
    stads = sorted(stads, key=lambda s: stad_totals[s], reverse=True)

    lookup = {(r["stadium_id"], r["poste"]): float(r["volume_m3"]) for r in rows}
    matrix = np.array([[lookup.get((s, p), 0.0) for p in postes] for s in stads])

    fig, ax = plt.subplots(figsize=(15, 9), facecolor="white")
    ax.set_facecolor("white")

    cmap = _fifa_cmap(light="#EEF1FB", dark=F_NAVY)
    im   = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0)

    ax.set_xticks(range(len(postes)))
    ax.set_xticklabels(postes, rotation=35, ha="right", fontsize=9.5)
    ax.set_yticks(range(len(stads)))
    ax.set_yticklabels(stads, fontsize=9.5)

    vmax = matrix.max()
    for i in range(len(stads)):
        for j in range(len(postes)):
            v = matrix[i, j]
            txt_col = "white" if v > vmax * 0.52 else F_NAVY
            ax.text(j, i, f"{v:.1f}" if v > 0 else "—",
                    ha="center", va="center",
                    fontsize=8, color=txt_col,
                    fontweight="bold" if v > 0 else "normal")

    cbar = plt.colorbar(im, ax=ax, shrink=0.85, pad=0.01)
    cbar.set_label("Volume (m³)", color=F_NAVY)
    cbar.ax.yaxis.set_tick_params(color=F_NAVY)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=F_NAVY)
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    ax.grid(False)
    _title_block(ax,
                 "Part I — Demand heatmap: stadium × equipment type (poste)",
                 "Interior and LED perimeter dominate; wayfinding & pitch-side are negligible")
    fig.tight_layout()
    _footer(fig, "stadium_demand_by_poste.csv")
    _save(fig, "part1_demand_heatmap.png")


def fig_setup_comparison():
    rows = _read_results_csv("part1_setup_comparison.csv")

    short_label = {
        "Baseline (LED direct, depots, weight, LCL)": "Baseline\n(LED direct,\nweight, LCL)",
        "LED via depot (no direct)":                  "LED via\ndepot",
        "Volume-only (no weight constraint)":          "Volume\nonly",
        "FCL-only (no LCL)":                          "FCL only\n(no LCL)",
    }
    labels    = [short_label.get(r["setup"], r["setup"]) for r in rows]
    costs     = [float(r["total_cost_usd"]) for r in rows]
    feu_tots  = [float(r["feu_total"])      for r in rows]
    baseline  = costs[0]

    colors = []
    for c in costs:
        if c < baseline - 1:   colors.append(C_SAVINGS)
        elif c > baseline + 1: colors.append(C_EXTRA)
        else:                  colors.append(C_BASELINE)

    x   = np.arange(len(labels))
    fig, ax1 = plt.subplots(figsize=(11, 6.5))

    bars = ax1.bar(x, costs, color=colors, edgecolor="white",
                   linewidth=0.5, width=0.52, alpha=0.92)
    ax1.set_ylabel("Total cost (USD)", color=F_NAVY)
    ax1.tick_params(axis="y", labelcolor=F_NAVY)
    ax1.set_ylim(0, max(costs) * 1.25)

    for i, (bar, c) in enumerate(zip(bars, costs)):
        delta = c - baseline
        sign  = "+" if delta >= 0 else ""
        lab   = f"${c:,.0f}\n({sign}{delta:,.0f})" if i > 0 else f"${c:,.0f}\n(baseline)"
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + max(costs) * 0.015,
                 lab, ha="center", va="bottom",
                 fontsize=8.5, color=F_NAVY, fontweight="bold")

    ax2 = ax1.twinx()
    ax2.plot(x, feu_tots, "D--", color=F_PURPLE, lw=2, ms=10,
             markerfacecolor=F_PURPLE, markeredgecolor="white",
             markeredgewidth=1.5, label="Total FEU", zorder=5)
    for i, f in enumerate(feu_tots):
        ax2.text(i, f + 2.5, f"{int(f)} FEU",
                 ha="center", color=F_PURPLE, fontsize=9, fontweight="bold")
    ax2.set_ylabel("Total FEU (40 ft containers)", color=F_PURPLE)
    ax2.tick_params(axis="y", labelcolor=F_PURPLE)
    ax2.set_ylim(0, max(feu_tots) * 1.35)
    ax2.spines["top"].set_visible(False)

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9.5)
    _clean_ax(ax1, "y")

    legend_els = [
        mpatches.Patch(color=C_BASELINE, label="Baseline"),
        mpatches.Patch(color=C_SAVINGS,  label="Cheaper than baseline"),
        mpatches.Patch(color=C_EXTRA,    label="More expensive"),
        Line2D([0], [0], color=F_PURPLE, marker="D", lw=2, ls="--",
               markersize=8, label="FEU count"),
    ]
    ax1.legend(handles=legend_els, loc="upper left", fontsize=8.5)
    _title_block(ax1,
                 "Part I — Setup comparison across 4 configurations",
                 "Volume-only saves $134k (−29 %) but ignores realistic 26 t weight limits")
    fig.tight_layout()
    _footer(fig, "part1_setup_comparison.csv")
    _save(fig, "part1_setup_comparison.png")


def fig_part1_sensitivity_tornado():
    rows     = _read_results_csv("part1_sensitivity.csv")
    baseline = 458_626.0

    params: dict[str, list[tuple[str, float]]] = {}
    for r in rows:
        params.setdefault(r["parameter"], []).append((r["value"], float(r["total_cost_usd"])))

    entries = []
    for param, vals in params.items():
        costs = [c for _, c in vals]
        lo    = min(costs) - baseline
        hi    = max(costs) - baseline
        entries.append((param, lo, hi))
    entries.sort(key=lambda e: abs(e[1]) + abs(e[2]), reverse=True)

    friendly = {
        "weight_constraint": "Weight constraint\n(on vs off)",
        "led_routing":       "LED routing\n(direct vs via depot)",
        "lcl_policy":        "LCL policy\n(allowed vs FCL-only)",
    }

    fig, ax = plt.subplots(figsize=(11, 5))
    y = np.arange(len(entries))
    h = 0.46

    for i, (param, lo, hi) in enumerate(entries):
        label = friendly.get(param, param)
        if lo < -1:
            ax.barh(i, lo, height=h, left=0, color=C_SAVINGS, alpha=0.92, edgecolor="white")
            ax.text(lo - 6000, i, f"−${abs(lo):,.0f}", va="center",
                    ha="right", fontsize=9, color=C_SAVINGS, fontweight="bold")
        if hi > 1:
            ax.barh(i, hi, height=h, left=0, color=C_EXTRA, alpha=0.92, edgecolor="white")
            ax.text(hi + 6000, i, f"+${abs(hi):,.0f}", va="center",
                    ha="left", fontsize=9, color=C_EXTRA, fontweight="bold")
        # parameter labels positioned safely RIGHT of the axis (positive side)
        ax.text(15_000, i, label, va="center", ha="left",
                fontsize=10, color=F_NAVY, fontweight="bold")

    ax.axvline(0, color=F_NAVY, lw=1.5, zorder=5)
    ax.set_yticks(y)
    ax.set_yticklabels([""] * len(entries))
    ax.set_xlabel("Change vs baseline  ($458,626)", fontsize=10)
    ax.set_facecolor("#FAFBFE")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(True, axis="x", alpha=0.5)
    ax.set_xlim(-185_000, 90_000)

    legend_els = [
        mpatches.Patch(color=C_SAVINGS, label="Cost reduction vs baseline"),
        mpatches.Patch(color=C_EXTRA,   label="Cost increase vs baseline"),
    ]
    ax.legend(handles=legend_els, loc="lower left", fontsize=9)
    _title_block(ax,
                 "Part I — One-at-a-time sensitivity tornado",
                 "The weight constraint dominates: turning it off would save $134k")
    fig.tight_layout()
    _footer(fig, "part1_sensitivity.csv")
    _save(fig, "part1_sensitivity_tornado.png")


def fig_soft_flow_matrix():
    rows = _read_results_csv("part1_flows_soft.csv")

    stad_order = ["STAD_SF", "STAD_SEA", "STAD_VAN", "STAD_LA",
                  "STAD_GDL", "STAD_MTY", "STAD_MEX",
                  "STAD_DAL", "STAD_HOU",
                  "STAD_KC",  "STAD_ATL",
                  "STAD_MIA", "STAD_TOR",
                  "STAD_NY_NJ", "STAD_PHI", "STAD_BOS"]
    short_s = {s: s.replace("STAD_", "") for s in stad_order}

    depot_order = ["LAX_DEPOT_NODE", "EWR_DEPOT_NODE"]
    short_d = {"LAX_DEPOT_NODE": "LAX depot\n(West / Central)",
               "EWR_DEPOT_NODE": "EWR depot\n(East)"}

    lookup       = {(r["depot_node"], r["stadium_node"]): float(r["volume_m3"]) for r in rows}
    stads_in_sol = {r["stadium_node"] for r in rows}
    stads_used   = [s for s in stad_order if s in stads_in_sol]

    matrix = np.array(
        [[lookup.get((d, s), 0.0) for s in stads_used] for d in depot_order]
    )

    fig, ax = plt.subplots(figsize=(14, 4.0), facecolor="white")
    ax.set_facecolor("white")

    cmap = _fifa_cmap(light="#EEF4FF", dark=F_NAVY)
    im   = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0)

    ax.set_xticks(range(len(stads_used)))
    ax.set_xticklabels([short_s[s] for s in stads_used],
                       rotation=35, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(depot_order)))
    ax.set_yticklabels([short_d[d] for d in depot_order], fontsize=9)

    vmax = matrix.max()
    for i in range(len(depot_order)):
        for j in range(len(stads_used)):
            v = matrix[i, j]
            tc = "white" if v > vmax * 0.55 else F_NAVY
            txt = f"{v:.0f}" if v > 0 else "—"
            ax.text(j, i, txt, ha="center", va="center",
                    fontsize=9, color=tc,
                    fontweight="bold" if v > 0 else "normal")

    cbar = plt.colorbar(im, ax=ax, label="Volume (m³)", shrink=0.85, pad=0.01)
    cbar.ax.yaxis.set_tick_params(color=F_NAVY)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=F_NAVY)
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    ax.grid(False)

    _title_block(ax,
                 "Part I — Soft-goods flow matrix (depot → stadium)",
                 "LAX serves West/Central, EWR serves East; KC is the only split venue")
    fig.tight_layout()
    _footer(fig, "part1_flows_soft.csv")
    _save(fig, "part1_flow_matrix.png")


def fig_cost_donut():
    s   = _load_json("part1_summary.json")
    cb  = s["cost_breakdown"]
    tot = s["total_cost"]

    friendly = {
        "sea":                    "Ocean freight",
        "depot_fixed":            "Depot fixed cost",
        "depot_handling":         "Depot handling",
        "truck_port_depot":       "Truck port→depot",
        "truck_depot_stadium":    "Truck depot→stadium",
        "truck_port_stadium_led": "Truck port→stadium (LED)",
    }

    # Aggregate small slices (<2 %) into "Other"
    threshold = 0.02 * tot
    big_keys   = [k for k in cb if cb[k] >= threshold]
    small_sum  = sum(cb[k] for k in cb if cb[k] < threshold)
    sizes      = [cb[k] for k in big_keys] + ([small_sum] if small_sum > 0 else [])
    labels     = [friendly[k] for k in big_keys] + (["Other (<2 %)"] if small_sum > 0 else [])
    colors     = COST_COLORS[:len(big_keys)] + ([C_NEUTRAL] if small_sum > 0 else [])

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")
    ax.set_facecolor("white")

    wedges, _ = ax.pie(
        sizes, labels=None, colors=colors,
        startangle=135,
        wedgeprops={"width": 0.56, "edgecolor": "white", "linewidth": 2.0},
    )

    for wedge, v in zip(wedges, sizes):
        pct = 100.0 * v / tot
        if pct >= 4.0:
            ang = (wedge.theta1 + wedge.theta2) / 2
            rx  = 0.68 * np.cos(np.radians(ang))
            ry  = 0.68 * np.sin(np.radians(ang))
            c   = colors[sizes.index(v)]
            txt_col = "white" if c in (F_NAVY, F_PURPLE, F_BLUE) else F_NAVY
            ax.text(rx, ry, f"{pct:.1f}%",
                    ha="center", va="center",
                    fontsize=10, fontweight="bold", color=txt_col)

    legend_labels = [f"{l}  —  ${v:,.0f}" for l, v in zip(labels, sizes)]
    ax.legend(wedges, legend_labels,
              loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=9)

    ax.text(0,  0.10, f"${tot/1e3:.0f}k",
            ha="center", va="center",
            fontsize=18, fontweight="bold", color=F_NAVY)
    ax.text(0, -0.10, f"{int(s['feu_total'])} FEU",
            ha="center", va="center", fontsize=11, color=F_PURPLE, fontweight="bold")

    ax.set_title("Part I — Cost by component\nOcean freight is 68 % of total",
                 fontsize=13, fontweight="bold", color=F_NAVY, pad=10)
    fig.tight_layout()
    _footer(fig, "part1_summary.json")
    _save(fig, "part1_cost_donut.png")


def fig_feu_efficiency():
    """B1 — visualises how full each FEU class is along volume / weight axes."""
    feu_v = dl.FEU_VOLUME_M3
    feu_w = dl.FEU_PAYLOAD_T
    rho_led  = dl.RHO_LED
    rho_soft = dl.RHO_SOFT

    classes = ["LED", "Soft goods"]
    densities = [rho_led, rho_soft]

    vol_pct = [100.0, 100.0]  # both could fill volume
    wt_at_full_vol = [feu_v * d for d in densities]  # weight if you filled to 67 m³
    wt_pct = [100.0 * w / feu_w for w in wt_at_full_vol]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    x = np.arange(len(classes))
    w = 0.35

    bars_v = ax.bar(x - w / 2, vol_pct, w, color=F_LBLUE,
                    label="Volume fill (% of 67 m³)", edgecolor="white")
    bars_w = ax.bar(x + w / 2, wt_pct,  w, color=C_LED,
                    label="Weight fill (% of 26 t)", edgecolor="white")

    ax.axhline(100, color=F_RED, lw=1.6, ls="--",
               label="100 % container limit", zorder=4)

    for bar, val in zip(bars_v, vol_pct):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 5,
                f"{val:.0f}%", ha="center", fontsize=10, fontweight="bold", color=F_NAVY)
    for bar, val in zip(bars_w, wt_pct):
        col = F_RED if val > 100 else F_NAVY
        ax.text(bar.get_x() + bar.get_width() / 2, val + 5,
                f"{val:.0f}%", ha="center", fontsize=10, fontweight="bold", color=col)

    # density annotation under each class (after the bars, in tick labels)
    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"{c}\n(density {d:.2f} t/m³)" for c, d in zip(classes, densities)],
        fontsize=11)
    ax.set_ylabel("Fill fraction (% of FEU capacity)")
    ax.set_ylim(0, 320)
    _clean_ax(ax, "y")
    ax.legend(loc="upper right", fontsize=9)
    _title_block(ax,
                 "Part I — FEU fill efficiency: weight binds before volume for LED",
                 "If you filled 67 m³ of LED, you'd be at 256 % of the 26 t weight limit")
    fig.tight_layout()
    _footer(fig, "data_loader.py constants (FEU 67 m³ / 26 t, ρ_LED=0.99, ρ_soft=0.46)")
    _save(fig, "part1_feu_efficiency.png")


# ============================================================================
# === Part I conceptual diagrams ===
# ============================================================================

def fig_network_architecture():
    """C1 — boxes-and-arrows schematic of the LRP network."""
    fig, ax = plt.subplots(figsize=(13, 6), facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")

    # Column centres
    cx = {"china": 8, "port": 32, "depot": 60, "stad": 88}

    def box(x, y, w, h, text, facecolor, edgecolor=F_NAVY, text_color="white", fontsize=11, fontweight="bold"):
        rect = FancyBboxPatch((x - w/2, y - h/2), w, h,
                              boxstyle="round,pad=0.4,rounding_size=0.6",
                              facecolor=facecolor, edgecolor=edgecolor,
                              linewidth=1.5, alpha=0.95)
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center",
                fontsize=fontsize, color=text_color, fontweight=fontweight)

    # Boxes
    box(cx["china"], 28, 12, 8,
        "CHINA\nproduction\n(Shanghai)", F_NAVY, text_color="white")

    # Ports group
    box(cx["port"], 38, 13, 5, "Port LA / LB",    F_LIME, text_color=F_NAVY)
    box(cx["port"], 30, 13, 5, "Port NY / NJ",    F_LIME, text_color=F_NAVY)
    box(cx["port"], 22, 13, 5, "Port Vancouver",  F_LIME, text_color=F_NAVY)

    # Depots group
    box(cx["depot"], 34, 12, 5, "LAX depot\n(West / Central)", F_PURPLE, text_color="white", fontsize=10)
    box(cx["depot"], 24, 12, 5, "EWR depot\n(East)",           F_PURPLE, text_color="white", fontsize=10)

    # Stadiums box
    box(cx["stad"], 29, 12, 14,
        "16 stadiums\n\nUSA (11)\nMexico (3)\nCanada (2)",
        C_LED, text_color="white", fontsize=11)

    # Arrows: china → ports (3 dashed arrows)
    for py in (38, 30, 22):
        arr = FancyArrowPatch((cx["china"] + 6, 28), (cx["port"] - 6.5, py),
                              arrowstyle="->", lw=1.4, color=F_NAVY,
                              connectionstyle="arc3,rad=0.05", mutation_scale=14)
        ax.add_patch(arr)
    ax.text((cx["china"] + cx["port"]) / 2, 44.5,
            "Ocean (FCL + LCL)", ha="center", fontsize=10,
            color=F_NAVY, fontweight="bold", style="italic")

    # Port → depot (soft solid)
    for py, dy in [(38, 34), (30, 34), (30, 24), (22, 34)]:
        arr = FancyArrowPatch((cx["port"] + 6.5, py), (cx["depot"] - 6, dy),
                              arrowstyle="->", lw=1.2, color=F_LBLUE,
                              connectionstyle="arc3,rad=0.05", mutation_scale=12)
        ax.add_patch(arr)

    # Depot → stadium (soft)
    for dy in (34, 24):
        arr = FancyArrowPatch((cx["depot"] + 6, dy), (cx["stad"] - 6.5, 29),
                              arrowstyle="->", lw=1.6, color=F_LBLUE,
                              connectionstyle="arc3,rad=0.0", mutation_scale=14)
        ax.add_patch(arr)

    # Port → stadium DIRECT (LED, dashed lime)
    for py in (38, 30, 22):
        arr = FancyArrowPatch((cx["port"] + 6.5, py), (cx["stad"] - 6.5, 29),
                              arrowstyle="->", lw=1.4, color=F_LIME,
                              connectionstyle="arc3,rad=-0.20", mutation_scale=12,
                              linestyle="--")
        ax.add_patch(arr)

    # Stage labels at top
    ax.text(cx["china"], 6.5, "Origin",  ha="center", fontsize=11, color=F_NAVY, fontweight="bold")
    ax.text(cx["port"],  6.5, "Sea gateway", ha="center", fontsize=11, color=F_NAVY, fontweight="bold")
    ax.text(cx["depot"], 6.5, "Cross-dock depot", ha="center", fontsize=11, color=F_NAVY, fontweight="bold")
    ax.text(cx["stad"],  6.5, "Demand", ha="center", fontsize=11, color=F_NAVY, fontweight="bold")

    # Flow legend (bottom)
    ax.text(50, 2.5,
            "—— Soft goods: port → depot → stadium       "
            "− − LED: direct port → stadium (heavy, FCL-only)",
            ha="center", fontsize=10, color=F_NAVY)

    _title_block(ax,
                 "Part I — Network architecture",
                 "Two material classes  ·  Two routing strategies  ·  One integrated LRP")
    fig.tight_layout()
    _footer(fig, "Schematic — derived from src/part1_lrp/model.py")
    _save(fig, "part1_network_architecture.png")


def fig_feu_constraint_box():
    """C3 — geometric view of the multidim FEU constraint."""
    feu_v = dl.FEU_VOLUME_M3   # 67 m³
    feu_w = dl.FEU_PAYLOAD_T   # 26 t
    rho_led  = dl.RHO_LED      # 0.994
    rho_soft = dl.RHO_SOFT     # 0.46

    fig, ax = plt.subplots(figsize=(9, 6.5), facecolor="white")
    ax.set_facecolor("#FAFBFE")

    # Container envelope
    rect = Rectangle((0, 0), feu_v, feu_w,
                     facecolor="#EEF1FB", edgecolor=F_NAVY, lw=2.0, zorder=2)
    ax.add_patch(rect)
    ax.text(feu_v / 2, feu_w * 1.05,
            f"FEU envelope: {feu_v:.0f} m³ × {feu_w:.0f} t",
            ha="center", fontsize=11, fontweight="bold", color=F_NAVY)

    # Density rays from origin
    x_max = feu_v * 1.05
    v_led = np.linspace(0, x_max, 100)
    w_led = v_led * rho_led
    v_soft = np.linspace(0, x_max, 100)
    w_soft = v_soft * rho_soft
    ax.plot(v_led,  w_led,  color=F_BLUE,  lw=2.4, label=f"LED density  {rho_led:.2f} t/m³", zorder=4)
    ax.plot(v_soft, w_soft, color=F_LBLUE, lw=2.4, label=f"Soft goods density  {rho_soft:.2f} t/m³", zorder=4)

    # Binding-point markers
    led_v_at_max_w = feu_w / rho_led  # = 26.2 m³
    soft_v_at_max_w = feu_w / rho_soft  # = 56.5 m³

    ax.scatter([led_v_at_max_w], [feu_w], s=180, color=F_BLUE,
               edgecolors="white", lw=1.8, zorder=6)
    ax.annotate(f"LED hits 26 t at {led_v_at_max_w:.1f} m³\n"
                f"({100 * led_v_at_max_w / feu_v:.0f} % volume used)",
                xy=(led_v_at_max_w, feu_w),
                xytext=(led_v_at_max_w - 18, feu_w + 18),
                fontsize=9, color=F_BLUE, fontweight="bold",
                arrowprops={"arrowstyle": "->", "color": F_BLUE, "lw": 1.4})

    ax.scatter([soft_v_at_max_w], [feu_w], s=180, color=F_LBLUE,
               edgecolors=F_NAVY, lw=1.4, zorder=6)
    ax.annotate(f"Soft hits 26 t at {soft_v_at_max_w:.1f} m³\n"
                f"({100 * soft_v_at_max_w / feu_v:.0f} % volume used)",
                xy=(soft_v_at_max_w, feu_w),
                xytext=(soft_v_at_max_w - 20, feu_w - 14),
                fontsize=9, color=F_NAVY, fontweight="bold",
                arrowprops={"arrowstyle": "->", "color": F_NAVY, "lw": 1.4})

    # Shaded forbidden region (light red)
    ax.fill_between([0, x_max], feu_w, feu_w * 2.7, color=F_RED, alpha=0.07, zorder=1)
    ax.text(x_max * 0.5, feu_w * 2.4,
            "OVERWEIGHT — outside FEU envelope",
            ha="center", fontsize=11, color=F_RED, style="italic", fontweight="bold")

    ax.set_xlim(0, x_max)
    ax.set_ylim(0, feu_w * 2.7)
    ax.set_xlabel("Volume (m³)")
    ax.set_ylabel("Weight (t)")
    _clean_ax(ax, "both")
    ax.grid(True, alpha=0.4)
    ax.legend(loc="upper left", fontsize=9)
    _title_block(ax,
                 "Part I — Multidimensional FEU constraint",
                 "LED reaches weight ceiling at 39 % volume fill → binds weight, not volume")
    fig.tight_layout()
    _footer(fig, "Geometric construction — FEU constants and material densities")
    _save(fig, "part1_feu_constraint_box.png")


# ============================================================================
# === Part II analytical ===
# ============================================================================

def fig_part2_stage_split():
    r = solve_stochastic(verbose=False)

    fig, ax = plt.subplots(figsize=(7, 5.5))
    ax.bar("Expected cost", r["stage1_cost"], color=C_STAGE1, edgecolor="white",
           label=f"Stage-1 anticipatory  (${r['stage1_cost']:,.0f})")
    ax.bar("Expected cost", r["stage2_expected_cost"], bottom=r["stage1_cost"],
           color=C_STAGE2, edgecolor="white",
           label=f"Stage-2 reactive  (${r['stage2_expected_cost']:,.0f})")

    ax.text(0, r["stage1_cost"] / 2,
            f"Stage-1\n${r['stage1_cost']/1e3:.0f}k",
            ha="center", va="center",
            color="white", fontsize=11, fontweight="bold")
    ax.text(0, r["stage1_cost"] + r["stage2_expected_cost"] / 2,
            f"Stage-2\n${r['stage2_expected_cost']/1e3:.0f}k",
            ha="center", va="center",
            color=F_NAVY, fontsize=11, fontweight="bold")

    ax.set_ylabel("USD")
    ax.set_ylim(0, r["total_expected_cost"] * 1.15)
    ax.set_xticks([])
    _clean_ax(ax, "y")
    ax.legend(loc="upper right")
    _title_block(ax,
                 "Part II — Two-stage cost split",
                 f"Total ${r['total_expected_cost']:,.0f}  ·  "
                 f"{r['n_forced']} / 16 matches forced anticipatory")
    fig.tight_layout()
    _footer(fig, "solve_stochastic()")
    _save(fig, "part2_stage_split.png")


def fig_part2_feasibility():
    from datetime import date
    road  = dl.load_road_edges()
    prod  = dl.load_production_sites()
    sites = [n for n in prod if n != "PROD_CHINA_SHANGHAI"]
    GSE   = date(2026, 6, 27)

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
        ts  = [road[(j, venue)]["transit_time_days"] for j in sites
               if (j, venue) in road and road[(j, venue)]["transit_time_days"] is not None]
        matches.append(int(rr["match"]))
        windows.append(win)
        mintransit.append(min(ts) if ts else None)

    # Filter out matches with no transit data (none expected with our data but be safe)
    keep = [i for i, t in enumerate(mintransit) if t is not None]
    matches    = [matches[i]    for i in keep]
    windows    = [windows[i]    for i in keep]
    mintransit = [mintransit[i] for i in keep]

    forced_idx = [i for i, (w, t) in enumerate(zip(windows, mintransit))
                  if t + 1 > w]

    fig, ax = plt.subplots(figsize=(13, 5.5))
    x = np.arange(len(matches))
    w = 0.38

    ax.bar(x - w / 2, windows,    w, label="Window (days from GSE)",
           color=C_REACTIVE, edgecolor="white", linewidth=0.5)
    ax.bar(x + w / 2, mintransit, w, label="Min transit time (best site)",
           color=C_FORCED, edgecolor="white", linewidth=0.5, alpha=0.92)

    for i in forced_idx:
        ax.bar(x[i] - w / 2, windows[i],    w, color=C_REACTIVE,
               edgecolor=F_RED, linewidth=2.2, zorder=4)
        ax.bar(x[i] + w / 2, mintransit[i], w, color=C_FORCED,
               edgecolor=F_RED, linewidth=2.2, zorder=4)

    ax.axhline(1, color=F_NAVY, ls=":", lw=1.5)

    ax.set_xticks(list(x))
    ax.set_xticklabels(matches, fontsize=8)
    ax.set_xlabel("R32 match number")
    ax.set_ylabel("Days")
    _clean_ax(ax, "y")

    legend_els = [
        mpatches.Patch(color=C_REACTIVE, label="Window (GSE → match)"),
        mpatches.Patch(color=C_FORCED,   label="Min transit (best site)"),
        mpatches.Patch(facecolor=C_REACTIVE, edgecolor=F_RED, linewidth=2,
                       label="Forced-anticipatory match"),
        Line2D([0], [0], color=F_NAVY, ls=":", lw=1.5, label="Production lead time (1 day)"),
    ]
    ax.legend(handles=legend_els, loc="upper right", fontsize=8.5)
    _title_block(ax,
                 "Part II — Feasibility: reactive supply needs  transit ≤ window − 1 day",
                 f"{len(forced_idx)} matches are forced anticipatory (red outline)")
    fig.tight_layout()
    _footer(fig, "scenario 0 + edges.csv + production_sites.csv")
    _save(fig, "part2_feasibility.png")


def fig_part2_sensitivity_tornado():
    rows     = _read_results_csv("part2_sensitivity.csv")
    baseline = 302_535.0

    params: dict[str, list[tuple[str, float]]] = {}
    for r in rows:
        params.setdefault(r["parameter"], []).append((r["value"], float(r["total_expected_cost_usd"])))

    entries = []
    for param, vals in params.items():
        costs = [c for _, c in vals]
        entries.append((param, min(costs) - baseline, max(costs) - baseline))
    entries.sort(key=lambda e: abs(e[1]) + abs(e[2]), reverse=True)

    friendly = {
        "production_cost_per_m2": "Production cost\n($/m²: $20 / $50 / $86)",
        "anticipatory_waste":     "Anticipatory waste factor\n(1× / 2× / 3×)",
        "production_days":        "Production days\n(0 d vs 1 d)",
        "storage_scenario":       "Storage scenario\n(low / base / high)",
    }

    fig, ax = plt.subplots(figsize=(11, 5.5))
    y = np.arange(len(entries))
    h = 0.46

    for i, (param, lo, hi) in enumerate(entries):
        label = friendly.get(param, param)
        if lo < -1:
            ax.barh(i, lo, height=h, left=0, color=C_SAVINGS, alpha=0.92, edgecolor="white")
            ax.text(lo - 8000, i, f"−${abs(lo):,.0f}", va="center",
                    ha="right", fontsize=9, color=C_SAVINGS, fontweight="bold")
        if hi > 1:
            ax.barh(i, hi, height=h, left=0, color=C_EXTRA, alpha=0.92, edgecolor="white")
            ax.text(hi + 8000, i, f"+${abs(hi):,.0f}", va="center",
                    ha="left", fontsize=9, color=C_EXTRA, fontweight="bold")
        # parameter labels positioned safely OUTSIDE the bar range
        ax.text(-340_000, i, label, va="center", ha="left",
                fontsize=10, color=F_NAVY, fontweight="bold")

    ax.axvline(0, color=F_NAVY, lw=1.5, zorder=5)
    ax.set_yticks(y)
    ax.set_yticklabels([""] * len(entries))
    ax.set_xlabel("Change vs baseline  ($302,535)", fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(True, axis="x", alpha=0.5)
    ax.set_xlim(-360_000, 300_000)

    legend_els = [
        mpatches.Patch(color=C_SAVINGS, label="Cost reduction vs baseline"),
        mpatches.Patch(color=C_EXTRA,   label="Cost increase vs baseline"),
    ]
    ax.legend(handles=legend_els, loc="lower left", fontsize=9)
    _title_block(ax,
                 "Part II — One-at-a-time sensitivity tornado",
                 "Production cost is the dominant lever; storage scenario is negligible")
    fig.tight_layout()
    _footer(fig, "part2_sensitivity.csv")
    _save(fig, "part2_sensitivity_tornado.png")


def fig_part2_stage_by_param():
    rows = _read_results_csv("part2_sensitivity.csv")

    friendly_param = {
        "production_cost_per_m2": "Production cost\n($/m²)",
        "anticipatory_waste":     "Anticipatory\nwaste",
        "production_days":        "Production\ndays",
        "storage_scenario":       "Storage\nscenario",
    }
    param_order = ["production_cost_per_m2", "anticipatory_waste",
                   "production_days", "storage_scenario"]

    groups: dict[str, list] = {p: [] for p in param_order}
    for r in rows:
        if r["parameter"] in groups:
            groups[r["parameter"]].append(r)

    bar_labels, s1_vals, s2_vals, totals = [], [], [], []
    y_positions = []
    y = 0.0

    group_ys: dict[str, list] = {p: [] for p in param_order}
    for p in param_order:
        for r in groups[p]:
            bar_labels.append(r["value"])
            s1_vals.append(float(r["stage1_cost_usd"]))
            s2_vals.append(float(r["stage2_cost_usd"]))
            totals.append(float(r["total_expected_cost_usd"]))
            y_positions.append(y)
            group_ys[p].append(y)
            y += 1.0
        y += 0.7

    fig, ax = plt.subplots(figsize=(12, 9))

    ax.barh(y_positions, s1_vals, height=0.6, color=C_STAGE1, edgecolor="white",
            label="Stage-1 (anticipatory)")
    ax.barh(y_positions, s2_vals, height=0.6, left=s1_vals, color=C_STAGE2,
            edgecolor="white", label="Stage-2 (reactive expected)")

    for yp, tot in zip(y_positions, totals):
        ax.text(tot + 4000, yp, f"${tot:,.0f}", va="center",
                fontsize=8.5, color=F_NAVY, fontweight="bold")

    ax.set_yticks(y_positions)
    ax.set_yticklabels(bar_labels, fontsize=9)
    ax.set_xlabel("USD")

    # group labels positioned safely to the left of bars (in axes coords)
    for p in param_order:
        if not group_ys[p]:
            continue
        mid = (group_ys[p][0] + group_ys[p][-1]) / 2
        # use a fixed x position derived from data limits
        ax.text(-0.13, mid, friendly_param[p],
                transform=ax.get_yaxis_transform(),
                ha="right", va="center",
                fontsize=10, color=F_NAVY, fontweight="bold")

    _clean_ax(ax, "x")
    ax.set_xlim(0, max(totals) * 1.22)
    ax.legend(loc="lower right", fontsize=9)
    _title_block(ax,
                 "Part II — Stage-1 / Stage-2 split by parameter variant",
                 "Production days swap costs between stages; storage barely moves either")
    fig.subplots_adjust(left=0.22)
    _footer(fig, "part2_sensitivity.csv")
    _save(fig, "part2_stage_by_param.png")


def fig_part2_prod_cost_curve():
    rows     = _read_results_csv("part2_sensitivity.csv")
    filtered = sorted(
        [r for r in rows if r["parameter"] == "production_cost_per_m2"],
        key=lambda r: float(r["total_expected_cost_usd"])
    )

    x_vals  = [float(r["value"].replace("$", "")) for r in filtered]
    totals  = [float(r["total_expected_cost_usd"]) for r in filtered]
    s1_vals = [float(r["stage1_cost_usd"])         for r in filtered]
    s2_vals = [float(r["stage2_cost_usd"])          for r in filtered]

    slope = (totals[-1] - totals[0]) / (x_vals[-1] - x_vals[0]) if len(x_vals) >= 2 else 0

    fig, ax = plt.subplots(figsize=(9, 5.5))

    ax.plot(x_vals, totals,  "o-",  color=F_NAVY,    lw=2.4, ms=10,
            markerfacecolor=F_NAVY, markeredgecolor="white", markeredgewidth=1.5,
            label="Total expected cost", zorder=4)
    ax.plot(x_vals, s1_vals, "s--", color=C_STAGE1,  lw=1.8, ms=8,
            markerfacecolor=C_STAGE1, markeredgecolor="white", markeredgewidth=1.2,
            label="Stage-1 (anticipatory)", zorder=3)
    ax.plot(x_vals, s2_vals, "^--", color=C_STAGE2,  lw=1.8, ms=8,
            markerfacecolor=C_STAGE2, markeredgecolor="white", markeredgewidth=1.2,
            label="Stage-2 (reactive)", zorder=3)

    for xv, tot in zip(x_vals, totals):
        ax.annotate(f"\\${tot/1e3:.0f}k", (xv, tot),
                    textcoords="offset points", xytext=(0, 12),
                    ha="center", fontsize=9.5, fontweight="bold", color=F_NAVY)

    ax.set_xlabel("Production cost (USD / m²)")
    ax.set_ylabel("Expected cost (USD)")
    ax.set_xticks(x_vals)
    ax.set_xticklabels([f"\\${int(v)}/m²" for v in x_vals], fontsize=10)
    _clean_ax(ax, "y")
    ax.legend(loc="upper left", fontsize=9)
    _title_block(ax,
                 "Part II — Sensitivity to production cost per m²",
                 f"Linear: every +\\$1/m² shifts total expected cost by ~\\${slope:,.0f}")
    fig.tight_layout()
    _footer(fig, "part2_sensitivity.csv (parameter = production_cost_per_m2)")
    _save(fig, "part2_prod_cost_curve.png")


def fig_anticipatory_by_match():
    """Rich window-vs-transit-vs-decision overlay."""
    from datetime import date
    r = solve_stochastic(verbose=False)

    forced_set = set(r["forced_anticipatory_matches"])
    match_ids  = sorted(r["match_venue"].keys())
    venues     = [r["match_venue"].get(mid, "?").replace("STAD_", "") for mid in match_ids]
    windows    = [r["match_window"].get(mid, 0) for mid in match_ids]

    road  = dl.load_road_edges()
    prod  = dl.load_production_sites()
    sites = [n for n in prod if n != "PROD_CHINA_SHANGHAI"]

    mintransit = []
    for mid in match_ids:
        v  = r["match_venue"][mid]
        ts = [road[(j, v)]["transit_time_days"] for j in sites
              if (j, v) in road and road[(j, v)]["transit_time_days"] is not None]
        mintransit.append(min(ts) if ts else None)

    fig, ax = plt.subplots(figsize=(13.5, 6))
    x = np.arange(len(match_ids))

    # Background bands: red shade for forced indices
    for i, mid in enumerate(match_ids):
        if mid in forced_set:
            ax.axvspan(i - 0.4, i + 0.4, color=F_RED, alpha=0.06, zorder=0)

    # Window as filled bar (green)
    ax.bar(x, windows, color=C_REACTIVE, edgecolor="white", width=0.62,
           alpha=0.85, label="Window (days from GSE to match)", zorder=2)
    # Transit time as smaller bar (red overlay)
    transit_plot = [t if t is not None else 0 for t in mintransit]
    ax.bar(x, transit_plot, color=F_RED, edgecolor="white", width=0.30,
           alpha=0.92, label="Min transit time (best site)", zorder=3)
    # Production lead-time floor (1 day)
    ax.axhline(1, color=F_NAVY, ls=":", lw=1.5, label="Production lead time (1 d)")

    for i, (win, mid) in enumerate(zip(windows, match_ids)):
        forced = mid in forced_set
        col = F_RED if forced else F_NAVY
        ax.text(i, win + 0.18, f"{win}d",
                ha="center", va="bottom", fontsize=8.5,
                color=col, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"M{mid}\n{v}" for mid, v in zip(match_ids, venues)],
        fontsize=8.5
    )
    ax.set_ylabel("Days")
    ax.set_ylim(0, max(windows) * 1.25)
    _clean_ax(ax, "y")

    legend_els = [
        mpatches.Patch(color=C_REACTIVE, label="Window (GSE → match day)"),
        mpatches.Patch(color=F_RED,      label="Min transit time (best site)"),
        mpatches.Patch(facecolor=F_RED, alpha=0.10,
                       label=f"Forced anticipatory ({len(forced_set)} matches)"),
        Line2D([0], [0], color=F_NAVY, ls=":", lw=1.5, label="Production lead time (1 d)"),
    ]
    ax.legend(handles=legend_els, loc="upper right", fontsize=8.5, ncol=2)
    _title_block(ax,
                 "Part II — Supply strategy by R32 match",
                 "Pink-shaded matches are forced anticipatory: window ≤ transit + 1 day")
    fig.tight_layout()
    _footer(fig, "solve_stochastic() + edges.csv")
    _save(fig, "part2_anticipatory_by_match.png")


def fig_part2_waste_curve():
    """B2 — cost vs anticipatory waste factor."""
    rows = _read_results_csv("part2_sensitivity.csv")
    filtered = sorted(
        [r for r in rows if r["parameter"] == "anticipatory_waste"],
        key=lambda r: float(r["total_expected_cost_usd"])
    )

    x_labels = [r["value"] for r in filtered]
    x_vals   = [float(v.replace("x", "")) for v in x_labels]
    totals   = [float(r["total_expected_cost_usd"]) for r in filtered]
    s1_vals  = [float(r["stage1_cost_usd"])         for r in filtered]
    s2_vals  = [float(r["stage2_cost_usd"])          for r in filtered]

    fig, ax = plt.subplots(figsize=(9, 5.5))

    ax.plot(x_vals, totals,  "o-",  color=F_NAVY,    lw=2.4, ms=10,
            markerfacecolor=F_NAVY, markeredgecolor="white", markeredgewidth=1.5,
            label="Total expected cost", zorder=4)
    ax.plot(x_vals, s1_vals, "s--", color=C_STAGE1,  lw=1.8, ms=8,
            markerfacecolor=C_STAGE1, markeredgecolor="white", markeredgewidth=1.2,
            label="Stage-1 (anticipatory)", zorder=3)
    ax.plot(x_vals, s2_vals, "^--", color=C_STAGE2,  lw=1.8, ms=8,
            markerfacecolor=C_STAGE2, markeredgecolor="white", markeredgewidth=1.2,
            label="Stage-2 (reactive)", zorder=3)

    for xv, tot in zip(x_vals, totals):
        ax.annotate(f"\\${tot/1e3:.0f}k", (xv, tot),
                    textcoords="offset points", xytext=(0, 12),
                    ha="center", fontsize=9.5, fontweight="bold", color=F_NAVY)

    slope = (totals[-1] - totals[0]) / (x_vals[-1] - x_vals[0])

    ax.set_xlabel("Anticipatory waste factor (×)")
    ax.set_ylabel("Expected cost (USD)")
    ax.set_xticks(x_vals)
    ax.set_xticklabels(x_labels, fontsize=10)
    _clean_ax(ax, "y")
    ax.legend(loc="upper left", fontsize=9)
    _title_block(ax,
                 "Part II — Sensitivity to anticipatory waste factor",
                 f"Each step (1× → 2× → 3×) costs ~\\${slope:,.0f} extra — pure cost of pre-positioning uncertainty")
    fig.tight_layout()
    _footer(fig, "part2_sensitivity.csv (parameter = anticipatory_waste)")
    _save(fig, "part2_waste_curve.png")


def fig_part2_production_days():
    """B3 — compare 0d vs 1d production lead time."""
    rows = _read_results_csv("part2_sensitivity.csv")
    filtered = [r for r in rows if r["parameter"] == "production_days"]
    filtered.sort(key=lambda r: r["value"])  # "0d" before "1d"

    labels  = [r["value"] for r in filtered]
    s1_vals = [float(r["stage1_cost_usd"]) for r in filtered]
    s2_vals = [float(r["stage2_cost_usd"]) for r in filtered]
    totals  = [float(r["total_expected_cost_usd"]) for r in filtered]
    forced  = [int(r["n_forced_anticipatory"])     for r in filtered]

    fig, ax = plt.subplots(figsize=(8, 6))
    x = np.arange(len(labels))
    w = 0.5
    ax.bar(x, s1_vals, w, color=C_STAGE1, edgecolor="white",
           label="Stage-1 (anticipatory)")
    ax.bar(x, s2_vals, w, bottom=s1_vals, color=C_STAGE2, edgecolor="white",
           label="Stage-2 (reactive expected)")

    for i, (tot, fc, s1) in enumerate(zip(totals, forced, s1_vals)):
        ax.text(i, tot + 8000, f"\\${tot:,.0f}",
                ha="center", fontsize=11, fontweight="bold", color=F_NAVY)
        ax.text(i, tot + 22_000, f"{fc} / 16 matches\nforced anticipatory",
                ha="center", fontsize=9, color=F_RED, fontweight="bold")
        # inside labels
        ax.text(i, s1 / 2, f"\\${s1/1e3:.0f}k",
                ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        ax.text(i, s1 + (tot - s1) / 2, f"\\${(tot - s1)/1e3:.0f}k",
                ha="center", va="center", color=F_NAVY, fontsize=10, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([f"{lbl} production\nlead time" for lbl in labels], fontsize=10)
    ax.set_ylabel("Expected cost (USD)")
    ax.set_ylim(0, max(totals) * 1.30)
    _clean_ax(ax, "y")
    ax.legend(loc="upper right", fontsize=9)
    _title_block(ax,
                 "Part II — Trade-off of production lead time",
                 "Same-day production halves forced-anticipatory matches but raises stage-2 trucking")
    fig.tight_layout()
    _footer(fig, "part2_sensitivity.csv (parameter = production_days)")
    _save(fig, "part2_production_days.png")


def fig_part2_reactive_sites():
    """B4 — production site usage frequency in stage-2."""
    r = solve_stochastic(verbose=False)
    usage = r.get("site_usage_freq", {})

    if not usage:
        print("Warning: site_usage_freq empty; skipping fig_part2_reactive_sites")
        return

    sites = sorted(usage.keys(), key=lambda k: usage[k], reverse=True)
    freqs = [usage[s] for s in sites]
    labels = [s.replace("PROD_", "").replace("_", " ") for s in sites]

    # Convert to "average matches served per scenario" (frequency * 16 / nscenarios)
    # The model returns freq = times_used / nscenarios so a value > 1 means avg >1 match per scenario
    fig, ax = plt.subplots(figsize=(10, 5.5))
    y = np.arange(len(sites))

    colors = [F_PURPLE, F_BLUE, F_LBLUE, F_LIME, C_NEUTRAL]
    palette = [colors[i % len(colors)] for i in range(len(sites))]

    bars = ax.barh(y, freqs, color=palette, edgecolor="white", height=0.6)
    for bar, f, lbl in zip(bars, freqs, labels):
        ax.text(bar.get_width() + max(freqs) * 0.015, bar.get_y() + bar.get_height() / 2,
                f"{f*100:.0f}% of scenarios",
                va="center", fontsize=9.5, fontweight="bold", color=F_NAVY)

    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Average reactive matches served per scenario")
    ax.set_xlim(0, max(freqs) * 1.30)
    ax.invert_yaxis()
    _clean_ax(ax, "x")
    _title_block(ax,
                 "Part II — Reactive production-site usage across 50 scenarios",
                 "WASS NC and WASS Tempe are critical hot spots — used in every scenario")
    fig.tight_layout()
    _footer(fig, "solve_stochastic() → site_usage_freq")
    _save(fig, "part2_reactive_sites.png")


def fig_part2_forced_map():
    """B5 — map of R32 venues with forced/reactive distinction."""
    coords = _node_coords()
    r      = solve_stochastic(verbose=False)
    forced_set = set(r["forced_anticipatory_matches"])

    # Build per-venue: any match at this venue forced => mark forced
    venue_status: dict[str, dict] = {}
    for mid, venue in r["match_venue"].items():
        if venue not in venue_status:
            venue_status[venue] = {"matches": [], "forced": False, "min_window": 99}
        venue_status[venue]["matches"].append(mid)
        if mid in forced_set:
            venue_status[venue]["forced"] = True
        w = r["match_window"].get(mid, 99)
        if w < venue_status[venue]["min_window"]:
            venue_status[venue]["min_window"] = w

    fig, ax = plt.subplots(figsize=(12, 7), facecolor="white")
    _draw_coastline(ax, fill=True)

    for venue, info in venue_status.items():
        if venue not in coords:
            continue
        lat, lon, _, name = coords[venue]
        col = F_RED if info["forced"] else F_LIME
        size = 280 if info["forced"] else 220
        ax.scatter(lon, lat, marker="o", color=col, s=size,
                   edgecolors=F_NAVY, linewidths=1.6, zorder=5, alpha=0.92)
        short = venue.replace("STAD_", "")
        ax.annotate(f"{short}\n(w={info['min_window']}d)",
                    (lon, lat), xytext=(7, 6), textcoords="offset points",
                    fontsize=8.5,
                    color=F_NAVY if not info["forced"] else F_RED,
                    fontweight="bold")

    legend_els = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=F_RED,
               markersize=14, markeredgecolor=F_NAVY,
               label=f"Forced anticipatory venue ({sum(1 for v in venue_status.values() if v['forced'])} venues)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=F_LIME,
               markersize=13, markeredgecolor=F_NAVY,
               label=f"Reactive venue ({sum(1 for v in venue_status.values() if not v['forced'])} venues)"),
    ]
    ax.legend(handles=legend_els, loc="lower left", fontsize=9,
              framealpha=0.95, edgecolor=C_NEUTRAL)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_xlim(-128, -60)
    ax.set_ylim(14, 51)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _title_block(ax,
                 "Part II — Forced-anticipatory venues across R32",
                 "Southern / Mexico venues with short windows must be pre-positioned")
    fig.tight_layout()
    _footer(fig, "solve_stochastic() + nodes.csv")
    _save(fig, "part2_forced_map.png")


def fig_part2_sensitivity_grid():
    """B6 — 2x2 grid of mini line charts, one per parameter."""
    rows = _read_results_csv("part2_sensitivity.csv")
    params = ["production_cost_per_m2", "anticipatory_waste", "production_days", "storage_scenario"]
    titles = {
        "production_cost_per_m2": "Production cost ($/m²)",
        "anticipatory_waste":     "Anticipatory waste factor",
        "production_days":        "Production days",
        "storage_scenario":       "Storage scenario",
    }
    baseline_val = {
        "production_cost_per_m2": "$50",
        "anticipatory_waste":     "2x",
        "production_days":        "1d",
        "storage_scenario":       "base",
    }

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    for ax, p in zip(axes.flat, params):
        filtered = [r for r in rows if r["parameter"] == p]
        # parse x for ordering
        def parse_x(v):
            v = v.replace("$", "").replace("x", "").replace("d", "")
            try:
                return float(v)
            except ValueError:
                return {"low": 0, "base": 1, "high": 2}.get(v, 0)
        filtered.sort(key=lambda r: parse_x(r["value"]))

        x = list(range(len(filtered)))
        totals = [float(r["total_expected_cost_usd"]) for r in filtered]
        labels = [r["value"] for r in filtered]

        ax.plot(x, totals, "o-", color=F_NAVY, lw=2.2, ms=9,
                markerfacecolor=F_NAVY, markeredgecolor="white", markeredgewidth=1.2)
        for xi, tot, lbl in zip(x, totals, labels):
            is_base = (lbl == baseline_val[p])
            ax.annotate(f"\\${tot/1e3:.0f}k",
                        (xi, tot), textcoords="offset points",
                        xytext=(0, 10),
                        ha="center", fontsize=9, fontweight="bold",
                        color=F_PURPLE if is_base else F_NAVY)

        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=9)
        ax.set_title(titles[p], fontsize=11, color=F_NAVY, fontweight="bold")
        ax.set_ylabel("USD")
        ax.set_facecolor("#FAFBFE")
        _clean_ax(ax, "y")

    fig.suptitle("Part II — Sensitivity grid: cost vs each parameter\n"
                 "Production cost is the only driver with large impact",
                 fontsize=13, fontweight="bold", color=F_NAVY, y=1.00)
    fig.tight_layout()
    _footer(fig, "part2_sensitivity.csv")
    _save(fig, "part2_sensitivity_grid.png")


# ============================================================================
# === Part II conceptual diagrams ===
# ============================================================================

def fig_two_stage_timeline():
    """C2 — horizontal timeline showing stage-1 vs stage-2 decision logic."""
    fig, ax = plt.subplots(figsize=(13, 6.5), facecolor="white")
    ax.set_facecolor("white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 40)
    ax.axis("off")

    # Timeline axis
    ax.plot([5, 95], [22, 22], color=F_NAVY, lw=2.5, zorder=3)

    # Events on timeline (top dots)
    events = [
        (15, "Group Stage End\n27 June 2026",  F_NAVY),
        (45, "R32 Draw\n28 June 2026",          F_PURPLE),
        (80, "R32 Matches\n28 Jun – 3 Jul",     F_BLUE),
    ]
    for x, label, col in events:
        ax.scatter([x], [22], s=180, color=col, edgecolors="white", lw=2, zorder=4)
        ax.annotate(label, (x, 22), xytext=(0, 18),
                    textcoords="offset points", ha="center",
                    fontsize=11, color=col, fontweight="bold")

    # Stage 1 region (before draw)
    rect1 = FancyBboxPatch((5, 5), 35, 10,
                           boxstyle="round,pad=0.4,rounding_size=0.6",
                           facecolor=F_PURPLE, edgecolor=F_NAVY,
                           linewidth=1.5, alpha=0.90)
    ax.add_patch(rect1)
    ax.text(22, 10,
            "STAGE 1 — Anticipatory decisions\n\n"
            "Before draw uncertainty resolves:\n"
            "• Produce nominative material (with 2× waste)\n"
            "• Ship & store at venue\n"
            "• Pay storage + production cost",
            ha="center", va="center", color="white", fontsize=10, fontweight="bold")

    # Stage 2 region (after draw)
    rect2 = FancyBboxPatch((50, 5), 45, 10,
                           boxstyle="round,pad=0.4,rounding_size=0.6",
                           facecolor=C_STAGE2, edgecolor=F_NAVY,
                           linewidth=1.5, alpha=0.90)
    ax.add_patch(rect2)
    ax.text(72.5, 10,
            "STAGE 2 — Reactive decisions  (scenario-dependent)\n\n"
            "After teams known:\n"
            "• Rush-produce exact material (no waste)\n"
            "• Truck from nearest production site\n"
            "• Only if  transit + 1d ≤ match window",
            ha="center", va="center", color=F_NAVY, fontsize=10, fontweight="bold")

    # Down-arrows from timeline to stage boxes
    arr1 = FancyArrowPatch((22, 22), (22, 15.2),
                           arrowstyle="->", lw=2, color=F_PURPLE,
                           mutation_scale=18)
    ax.add_patch(arr1)
    arr2 = FancyArrowPatch((72.5, 22), (72.5, 15.2),
                           arrowstyle="->", lw=2, color=C_STAGE2,
                           mutation_scale=18)
    ax.add_patch(arr2)

    # Note about forced anticipatory
    ax.text(50, 1.5,
            "When the match window is too short for reactive supply ⟹ the match is FORCED anticipatory in Stage 1.",
            ha="center", fontsize=10, color=F_RED, fontweight="bold", style="italic")

    _title_block(ax,
                 "Part II — Two-stage stochastic decision timeline",
                 "Stage-1 commits before uncertainty; Stage-2 reacts within each scenario")
    fig.tight_layout()
    _footer(fig, "Schematic — derived from src/part2_stochastic/model.py")
    _save(fig, "part2_two_stage_timeline.png")


# ============================================================================
# Entry point
# ============================================================================

def main():
    print("Generating Part I analytical figures...")
    fig_network_map()
    fig_cost_breakdown()
    fig_feu_by_class()
    fig_port_utilization()
    fig_stadium_demand()
    fig_demand_by_poste()
    fig_setup_comparison()
    fig_part1_sensitivity_tornado()
    fig_soft_flow_matrix()
    fig_cost_donut()
    fig_feu_efficiency()

    print("Generating Part I conceptual diagrams...")
    fig_network_architecture()
    fig_feu_constraint_box()

    print("Generating Part II analytical figures...")
    fig_part2_stage_split()
    fig_part2_feasibility()
    fig_part2_sensitivity_tornado()
    fig_part2_stage_by_param()
    fig_part2_prod_cost_curve()
    fig_anticipatory_by_match()
    fig_part2_waste_curve()
    fig_part2_production_days()
    fig_part2_reactive_sites()
    fig_part2_forced_map()
    fig_part2_sensitivity_grid()

    print("Generating Part II conceptual diagrams...")
    fig_two_stage_timeline()

    print(f"\nAll 25 figures written to {dl.FIGURES_DIR}")


if __name__ == "__main__":
    main()
