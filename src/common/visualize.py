"""
Visualisations — FIFA WC2026 Logistics (MGT-530, HEC Lausanne / EPFL E4S).

Colour palette: official FIFA WC2026 brand colours.
All figures are saved as PNG (130 dpi) into outputs/figures/.

Figures produced:
  Part I (deterministic LRP)
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

  Part II (two-stage stochastic)
    part2_stage_split.png
    part2_feasibility.png
    part2_sensitivity_tornado.png
    part2_stage_by_param.png
    part2_prod_cost_curve.png
    part2_anticipatory_by_match.png
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
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl
from part1_lrp.model import solve_lrp
from part2_stochastic.model import solve_stochastic


# ============================================================================
# FIFA WC2026 brand palette
# ============================================================================
F_PURPLE  = "#622EEA"   # purple
F_RED     = "#D31E03"   # red
F_LIME    = "#AEEA00"   # lime green
F_BLUE    = "#375AFE"   # bright blue
F_LBLUE   = "#8DBAFE"   # light blue
F_NAVY    = "#1A2688"   # dark navy

# Semantic aliases
C_LED        = F_BLUE
C_SOFT       = F_LBLUE
C_STAGE1     = F_PURPLE
C_STAGE2     = F_LBLUE
C_FORCED     = F_RED
C_REACTIVE   = F_LIME
C_SAVINGS    = F_LIME
C_EXTRA      = F_RED
C_BASELINE   = F_NAVY
C_SEA        = F_NAVY
C_NEUTRAL    = "#C8D0E0"   # light neutral for zero/background

# Cost-component colours (6 components)
COST_COLORS = [F_NAVY, F_PURPLE, F_BLUE, F_LBLUE, F_RED, F_LIME]

# ============================================================================
# Global matplotlib style
# ============================================================================
plt.rcParams.update({
    "font.family":            "DejaVu Sans",
    "font.size":              10,
    "axes.facecolor":         "#F5F6FA",
    "figure.facecolor":       "white",
    "axes.edgecolor":         F_NAVY,
    "axes.labelcolor":        F_NAVY,
    "axes.labelsize":         11,
    "axes.titlesize":         13,
    "axes.titleweight":       "bold",
    "axes.titlepad":          12,
    "axes.spines.top":        False,
    "axes.spines.right":      False,
    "axes.grid":              True,
    "grid.color":             "#DADCE8",
    "grid.linestyle":         "--",
    "grid.linewidth":         0.6,
    "grid.alpha":             0.8,
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
    """Remove top/right spines and set a subtle grid on one axis only."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(C_NEUTRAL)
    ax.spines["bottom"].set_color(C_NEUTRAL)
    ax.grid(True, axis=grid_axis)
    ax.grid(False, axis="x" if grid_axis == "y" else "y")


def _title_block(ax, title: str, subtitle: str = ""):
    """Bold title + optional grey subtitle."""
    full = title if not subtitle else f"{title}\n{subtitle}"
    ax.set_title(full, color=F_NAVY, fontsize=13, fontweight="bold", pad=14)


def _bar_label(ax, bars, fmt="{:.0f}", color=F_NAVY, offset=1.5, fontsize=9):
    """Annotate bar heights."""
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + offset,
                    fmt.format(h), ha="center", va="bottom",
                    fontsize=fontsize, color=color, fontweight="bold")


def _fifa_cmap(light="#EEF1FB", dark=F_NAVY):
    """Linear colourmap from light → FIFA navy."""
    return mcolors.LinearSegmentedColormap.from_list("fifa", [light, dark])


# ============================================================================
# Part I — original figures (redesigned)
# ============================================================================

def fig_network_map():
    coords   = _node_coords()
    r        = solve_lrp(verbose=False)

    fig, ax = plt.subplots(figsize=(12, 7), facecolor="white")
    ax.set_facecolor("#EEF1FB")

    # ---- all nodes (faint) -----------------------------------------------
    style_map = {
        "stadium":        ("o", C_LED,      45, 0.7),
        "candidate_depot":("s", F_PURPLE,  100, 0.35),
        "port_gateway":   ("^", C_SAVINGS, 130, 0.35),
        "production_site":("D", C_NEUTRAL,  28, 0.5),
    }
    for nid, (lat, lon, ntype, name) in coords.items():
        if ntype in style_map and "CHINA" not in nid:
            m, c, s, a = style_map[ntype]
            ax.scatter(lon, lat, marker=m, color=c, s=s, alpha=a,
                       edgecolors="white", linewidths=0.4, zorder=3)

    # ---- soft flows (port→depot→stadium, blue-grey) ----------------------
    for (d, sv), v in r["flows_soft_ds"].items():
        if d in coords and sv in coords:
            lw = 0.5 + 2.5 * v / 130
            ax.plot([coords[d][1], coords[sv][1]],
                    [coords[d][0], coords[sv][0]],
                    color=C_SOFT, lw=lw, alpha=0.55, zorder=2)

    # ---- LED direct flows (port→stadium, lime dashed) --------------------
    for (p, sv), v in r["flows_led_ps"].items():
        if p in coords and sv in coords:
            ax.plot([coords[p][1], coords[sv][1]],
                    [coords[p][0], coords[sv][0]],
                    color=C_SAVINGS, lw=1.1, alpha=0.5, ls="--", zorder=1)

    # ---- highlight open ports & depots ------------------------------------
    for p in r["ports_open"]:
        lat, lon = coords[p][0], coords[p][1]
        ax.scatter(lon, lat, marker="^", color=C_SAVINGS, s=310,
                   edgecolors=F_NAVY, linewidths=1.5, zorder=6)
    for d in r["depots_open"]:
        lat, lon = coords[d][0], coords[d][1]
        ax.scatter(lon, lat, marker="s", color=F_PURPLE, s=250,
                   edgecolors=F_NAVY, linewidths=1.5, zorder=6)
    # stadiums (filled bold)
    for nid, (lat, lon, ntype, _) in coords.items():
        if ntype == "stadium":
            ax.scatter(lon, lat, marker="o", color=C_LED, s=55,
                       edgecolors="white", linewidths=0.8, zorder=5)

    # ---- legend -----------------------------------------------------------
    legend_els = [
        mpatches.Patch(color=C_SAVINGS,  label="Open port (LED direct, dashed)"),
        mpatches.Patch(color=F_PURPLE,   label="Open depot (soft goods, solid)"),
        mpatches.Patch(color=C_LED,      label="Stadium"),
        mpatches.Patch(color=C_SOFT,     label="Soft-goods flow"),
        mpatches.Patch(color=C_SAVINGS,  label="LED direct flow"),
    ]
    ax.legend(handles=legend_els, loc="lower left", fontsize=8,
              framealpha=0.9, edgecolor=C_NEUTRAL)

    ax.set_xlabel("Longitude", fontsize=10)
    ax.set_ylabel("Latitude",  fontsize=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _title_block(ax,
                 f"Part I — Optimal supply network",
                 f"Total cost ${r['total_cost']:,.0f}  ·  {r['feu_total']:.0f} FEU  "
                 f"·  {len(r['ports_open'])} ports  ·  {len(r['depots_open'])} depots")
    fig.tight_layout()
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
        "truck_port_stadium_led": "Truck port→stadium\n(LED direct)",
    }

    fig, ax = plt.subplots(figsize=(9, 6))
    bottom = 0
    for k, v, c in zip(keys, vals, COST_COLORS):
        bar = ax.bar("Part I", v, bottom=bottom,
                     label=f"{friendly[k]}  (${v:,.0f})", color=c, edgecolor="white")
        # label inside segment if tall enough
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
    _title_block(ax, "Part I — Cost breakdown by component",
                 f"Total: ${r['total_cost']:,.0f}")
    fig.tight_layout()
    _save(fig, "part1_cost_breakdown.png")


def fig_feu_by_class():
    on  = solve_lrp(enforce_weight=True,  verbose=False)
    off = solve_lrp(enforce_weight=False, verbose=False)

    cases = ["Weight constraint ON\n(realistic, 26 t/FEU)",
             "Weight constraint OFF\n(volume-only, 67 m³/FEU)"]
    led  = [on["feu_led_total"],  off["feu_led_total"]]
    soft = [on["feu_soft_total"], off["feu_soft_total"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(cases))
    w = 0.5
    b1 = ax.bar(x, led,  w, label="LED FEU",  color=C_LED,  edgecolor="white")
    b2 = ax.bar(x, soft, w, bottom=led, label="Soft FEU", color=C_SOFT, edgecolor="white")

    for i, (l, s) in enumerate(zip(led, soft)):
        ax.text(i, l + s + 1.2, f"{int(l+s)} FEU",
                ha="center", fontsize=12, fontweight="bold", color=F_NAVY)
        ax.text(i, l / 2, f"{int(l)}",
                ha="center", va="center", fontsize=9, color="white", fontweight="bold")
        ax.text(i, l + s / 2, f"{int(s)}",
                ha="center", va="center", fontsize=9, color=F_NAVY, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(cases, fontsize=10)
    ax.set_ylabel("Number of 40 ft containers (FEU)")
    _clean_ax(ax, "y")
    ax.legend(loc="upper right")
    _title_block(ax,
                 "The LED weight effect: 26 t ceiling forces more containers",
                 f"${on['total_cost']:,.0f}  vs  ${off['total_cost']:,.0f}  "
                 f"(+${on['total_cost']-off['total_cost']:,.0f} / +{on['feu_total']-off['feu_total']:.0f} FEU)")
    fig.tight_layout()
    _save(fig, "part1_feu_by_class.png")


# ============================================================================
# Part I — new figures (redesigned)
# ============================================================================

def fig_port_utilization():
    s = _load_json("part1_summary.json")
    pd = s["ports_open"]

    short = {
        "PORT_LA_LB": "LA / Long Beach",
        "PORT_NY_NJ": "New York / NJ",
        "PORT_VAN":   "Vancouver",
    }
    port_order = list(pd.keys())
    labels   = [short.get(p, p) for p in port_order]
    feu_led  = [pd[p]["feu_led"]  for p in port_order]
    feu_soft = [pd[p]["feu_soft"] for p in port_order]
    lcl_vals = [pd[p]["lcl_soft"] for p in port_order]

    x = np.arange(len(labels))
    w = 0.32
    fig, ax = plt.subplots(figsize=(9, 5))

    b_led  = ax.bar(x - w / 2, feu_led,  w, label="LED FEU",  color=C_LED,  edgecolor="white", linewidth=0.5)
    b_soft = ax.bar(x + w / 2, feu_soft, w, label="Soft FEU", color=C_SOFT, edgecolor="white", linewidth=0.5)

    for bar in b_led:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.25,
                    f"{int(h)}", ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color=F_NAVY)
    for bar in b_soft:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.25,
                    f"{int(h)}", ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color=F_NAVY)

    # LCL footnote below x labels
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
                 f"Total: {int(s['feu_led_total'])} LED + {int(s['feu_soft_total'])} soft"
                 f" = {int(s['feu_total'])} FEU  ·  Italic = LCL overflow volume")
    fig.tight_layout()
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

    ax.barh(y, v_led,  h, label=f"LED perimeter (constant 67 m³)",
            color=C_LED,  edgecolor="white", linewidth=0.4)
    ax.barh(y, v_soft, h, left=v_led, label="Soft goods (variable by stadium)",
            color=C_SOFT, edgecolor="white", linewidth=0.4)

    for i, (tot, vl) in enumerate(zip(v_tot, v_led)):
        ax.text(tot + 1.5, i, f"{tot:.0f} m³",
                va="center", fontsize=8.5, color=F_NAVY, fontweight="bold")
        # small label inside LED bar
        ax.text(vl / 2, i, "LED", va="center", ha="center",
                fontsize=7, color="white", fontweight="bold")

    ax.set_yticks(y)
    ax.set_yticklabels(stads, fontsize=9)
    ax.set_xlabel("Volume (m³)")
    ax.set_xlim(0, max(v_tot) * 1.15)
    _clean_ax(ax, "x")
    ax.legend(loc="lower right", fontsize=9)
    _title_block(ax,
                 "Part I — Stadium demand by material class",
                 "Sorted by total volume  ·  LED is identical at every venue  ·  Soft goods vary by capacity")
    fig.tight_layout()
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

    fig, ax = plt.subplots(figsize=(14, 8), facecolor="white")
    ax.set_facecolor("white")

    cmap = _fifa_cmap(light="#EEF1FB", dark=F_NAVY)
    im   = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0)

    ax.set_xticks(range(len(postes)))
    ax.set_xticklabels(postes, rotation=38, ha="right", fontsize=8.5)
    ax.set_yticks(range(len(stads)))
    ax.set_yticklabels(stads, fontsize=8.5)

    vmax = matrix.max()
    for i in range(len(stads)):
        for j in range(len(postes)):
            v = matrix[i, j]
            txt_col = "white" if v > vmax * 0.52 else F_NAVY
            ax.text(j, i, f"{v:.1f}" if v > 0 else "—",
                    ha="center", va="center",
                    fontsize=6.5, color=txt_col,
                    fontweight="bold" if v > 0 else "normal")

    cbar = plt.colorbar(im, ax=ax, shrink=0.85, pad=0.01)
    cbar.set_label("Volume (m³)", color=F_NAVY)
    cbar.ax.yaxis.set_tick_params(color=F_NAVY)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=F_NAVY)

    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    _title_block(ax,
                 "Part I — Demand heatmap: stadium × equipment type",
                 "Sorted by total volume (descending)  ·  Colour intensity = volume (m³)")
    fig.tight_layout()
    _save(fig, "part1_demand_heatmap.png")


def fig_setup_comparison():
    rows = _read_results_csv("part1_setup_comparison.csv")

    short_label = {
        "Baseline (LED direct, depots, weight, LCL)": "Baseline",
        "LED via depot (no direct)":                  "LED via\ndepot",
        "Volume-only (no weight constraint)":          "Volume\nonly",
        "FCL-only (no LCL)":                          "FCL only",
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
    fig, ax1 = plt.subplots(figsize=(10, 6))

    bars = ax1.bar(x, costs, color=colors, edgecolor="white",
                   linewidth=0.5, width=0.52, alpha=0.92)
    ax1.set_ylabel("Total cost (USD)", color=F_NAVY)
    ax1.tick_params(axis="y", labelcolor=F_NAVY)
    ax1.set_ylim(0, max(costs) * 1.22)

    for i, (bar, c) in enumerate(zip(bars, costs)):
        delta = c - baseline
        sign  = "+" if delta >= 0 else ""
        lab   = f"${c:,.0f}\n({sign}{delta:,.0f})" if i > 0 else f"${c:,.0f}\n(baseline)"
        tc    = F_NAVY if colors[i] == C_SAVINGS else "white"
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + max(costs) * 0.015,
                 lab, ha="center", va="bottom",
                 fontsize=8.5, color=F_NAVY, fontweight="bold")

    ax2 = ax1.twinx()
    ax2.plot(x, feu_tots, "D--", color=F_PURPLE, lw=2, ms=9,
             markerfacecolor=F_PURPLE, markeredgecolor="white",
             markeredgewidth=1.2, label="Total FEU", zorder=5)
    for i, f in enumerate(feu_tots):
        ax2.text(i, f + 1.5, f"{int(f)} FEU",
                 ha="center", color=F_PURPLE, fontsize=8.5, fontweight="bold")
    ax2.set_ylabel("Total FEU (40 ft containers)", color=F_PURPLE)
    ax2.tick_params(axis="y", labelcolor=F_PURPLE)
    ax2.set_ylim(0, max(feu_tots) * 1.28)
    ax2.spines["top"].set_visible(False)

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    _clean_ax(ax1, "y")

    legend_els = [
        mpatches.Patch(color=C_BASELINE, label="Baseline"),
        mpatches.Patch(color=C_SAVINGS,  label="Cheaper than baseline"),
        mpatches.Patch(color=C_EXTRA,    label="More expensive"),
        mpatches.Patch(color=F_PURPLE,   label="FEU count (line)"),
    ]
    ax1.legend(handles=legend_els, loc="upper left", fontsize=8)
    _title_block(ax1,
                 "Part I — Setup comparison across 4 configurations",
                 "Cost (bars, left axis)  ·  FEU count (purple line, right axis)")
    fig.tight_layout()
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

    fig, ax = plt.subplots(figsize=(10, 4.5))
    y = np.arange(len(entries))
    h = 0.46

    for i, (param, lo, hi) in enumerate(entries):
        label = friendly.get(param, param)
        if lo < -1:
            ax.barh(i, lo, height=h, left=0, color=C_SAVINGS,  alpha=0.90, edgecolor="white")
            ax.text(lo - 3500, i, f"−${abs(lo):,.0f}", va="center",
                    ha="right", fontsize=9, color=C_SAVINGS, fontweight="bold")
        if hi > 1:
            ax.barh(i, hi, height=h, left=0, color=C_EXTRA, alpha=0.90, edgecolor="white")
            ax.text(hi + 3500, i, f"+${abs(hi):,.0f}", va="center",
                    ha="left", fontsize=9, color=C_EXTRA, fontweight="bold")
        ax.text(-8000, i, label, va="center", ha="right", fontsize=9.5, color=F_NAVY)

    ax.axvline(0, color=F_NAVY, lw=1.5, zorder=5)
    ax.set_yticks(y)
    ax.set_yticklabels([""] * len(entries))
    ax.set_xlabel("Change vs baseline  ($458,626)", fontsize=10)
    ax.set_facecolor("#F5F6FA")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(True, axis="x", alpha=0.5)
    ax.set_xlim(-165_000, 22_000)

    legend_els = [
        mpatches.Patch(color=C_SAVINGS, label="Cost reduction vs baseline"),
        mpatches.Patch(color=C_EXTRA,   label="Cost increase vs baseline"),
    ]
    ax.legend(handles=legend_els, loc="lower right", fontsize=9)
    _title_block(ax,
                 "Part I — One-at-a-time sensitivity tornado",
                 "Baseline = $458,626  ·  Bars show deviation")
    fig.tight_layout()
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

    fig, ax = plt.subplots(figsize=(14, 3.8), facecolor="white")
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
                    fontsize=8.5, color=tc,
                    fontweight="bold" if v > 0 else "normal")

    cbar = plt.colorbar(im, ax=ax, label="Volume (m³)", shrink=0.85, pad=0.01)
    cbar.ax.yaxis.set_tick_params(color=F_NAVY)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=F_NAVY)
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)

    _title_block(ax,
                 "Part I — Soft-goods flow matrix (depot → stadium)",
                 "West → East order  ·  LAX serves West/Central  ·  EWR serves East")
    fig.tight_layout()
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
    keys   = list(cb.keys())
    sizes  = [cb[k] for k in keys]
    labels = [friendly[k] for k in keys]

    fig, ax = plt.subplots(figsize=(9, 6), facecolor="white")
    ax.set_facecolor("white")

    wedges, _ = ax.pie(
        sizes,
        labels=None,
        colors=COST_COLORS,
        startangle=135,
        wedgeprops={"width": 0.56, "edgecolor": "white", "linewidth": 2.0},
    )

    # percentage labels inside each wedge (only if slice ≥ 3%)
    for wedge, v in zip(wedges, sizes):
        pct = 100.0 * v / tot
        if pct >= 3.0:
            ang = (wedge.theta1 + wedge.theta2) / 2
            rx  = 0.68 * np.cos(np.radians(ang))
            ry  = 0.68 * np.sin(np.radians(ang))
            c   = COST_COLORS[sizes.index(v)]
            txt_col = "white" if c in (F_NAVY, F_PURPLE, F_BLUE) else F_NAVY
            ax.text(rx, ry, f"{pct:.1f}%",
                    ha="center", va="center",
                    fontsize=9.5, fontweight="bold", color=txt_col)

    legend_labels = [f"{l}  —  ${v:,.0f}" for l, v in zip(labels, sizes)]
    ax.legend(wedges, legend_labels,
              loc="center left", bbox_to_anchor=(1.0, 0.5), fontsize=9)

    ax.text(0, 0, f"${tot/1e3:.0f}k",
            ha="center", va="center",
            fontsize=16, fontweight="bold", color=F_NAVY)
    ax.text(0, -0.22, "total",
            ha="center", va="center", fontsize=10, color=F_NAVY)

    ax.set_title("Part I — Cost by component\nOcean freight accounts for 68 % of total",
                 fontsize=13, fontweight="bold", color=F_NAVY, pad=14)
    fig.tight_layout()
    _save(fig, "part1_cost_donut.png")


# ============================================================================
# Part II — original figures (redesigned)
# ============================================================================

def fig_part2_stage_split():
    r = solve_stochastic(verbose=False)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar("Expected cost", r["stage1_cost"], color=C_STAGE1, edgecolor="white",
           label=f"Stage-1 anticipatory  (${r['stage1_cost']:,.0f})")
    ax.bar("Expected cost", r["stage2_expected_cost"], bottom=r["stage1_cost"],
           color=C_STAGE2, edgecolor="white",
           label=f"Stage-2 reactive  (${r['stage2_expected_cost']:,.0f})")

    # labels inside bars
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
                 f"Part II — Two-stage cost split",
                 f"Total expected cost ${r['total_expected_cost']:,.0f}  ·  "
                 f"{r['n_forced']} / 16 matches forced anticipatory")
    fig.tight_layout()
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

    # determine forced matches (mintransit >= window)
    forced_idx = [i for i, (w, t) in enumerate(zip(windows, mintransit))
                  if t is not None and t >= w]

    fig, ax = plt.subplots(figsize=(12, 5))
    x = np.arange(len(matches))
    w = 0.38

    bars_win = ax.bar(x - w / 2, windows,    w, label="Window (days from GSE to match)",
                      color=C_REACTIVE, edgecolor="white", linewidth=0.5)
    bars_tr  = ax.bar(x + w / 2, mintransit, w, label="Min transit (days, best site)",
                      color=C_FORCED,   edgecolor="white", linewidth=0.5, alpha=0.9)

    # highlight forced pairs
    for i in forced_idx:
        ax.bar(x[i] - w / 2, windows[i],    w, color=C_REACTIVE, edgecolor=F_RED, linewidth=2.0)
        ax.bar(x[i] + w / 2, mintransit[i], w, color=C_FORCED,   edgecolor=F_RED, linewidth=2.0)

    ax.axhline(1, color=F_NAVY, ls=":", lw=1.5,
               label="Production lead time = 1 day")

    ax.set_xticks(list(x))
    ax.set_xticklabels(matches, fontsize=8)
    ax.set_xlabel("R32 match number")
    ax.set_ylabel("Days")
    _clean_ax(ax, "y")

    legend_els = [
        mpatches.Patch(color=C_REACTIVE, label="Window (days GSE → match)"),
        mpatches.Patch(color=C_FORCED,   label="Min transit (best site)"),
        mpatches.Patch(facecolor=C_REACTIVE, edgecolor=F_RED, linewidth=2, label="Forced-anticipatory match"),
        plt.Line2D([0], [0], color=F_NAVY, ls=":", lw=1.5, label="Production lead time (1 day)"),
    ]
    ax.legend(handles=legend_els, loc="upper right", fontsize=8.5)
    _title_block(ax,
                 "Part II — Feasibility: reactive supply requires  transit ≤ window − 1 day",
                 "Red-outlined bars = matches forced anticipatory (transit + 1 > window)")
    fig.tight_layout()
    _save(fig, "part2_feasibility.png")


# ============================================================================
# Part II — new figures (redesigned)
# ============================================================================

def fig_part2_sensitivity_tornado():
    rows     = _read_results_csv("part2_sensitivity.csv")
    baseline = 302_535.0

    params: dict[str, list[tuple[str, float]]] = {}
    for r in rows:
        params.setdefault(r["parameter"], []).append((r["value"], float(r["total_expected_cost_usd"])))

    entries = []
    for param, vals in params.items():
        costs = [c for _, c in vals]
        lo    = min(costs) - baseline
        hi    = max(costs) - baseline
        entries.append((param, lo, hi))
    entries.sort(key=lambda e: abs(e[1]) + abs(e[2]), reverse=True)

    friendly = {
        "production_cost_per_m2": "Production cost\n($/m²: $20 / $50 / $86)",
        "anticipatory_waste":     "Anticipatory waste factor\n(1× / 2× / 3×)",
        "production_days":        "Production days\n(0 d vs 1 d)",
        "storage_scenario":       "Storage scenario\n(low / base / high)",
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    y = np.arange(len(entries))
    h = 0.46

    for i, (param, lo, hi) in enumerate(entries):
        label = friendly.get(param, param)
        if lo < -1:
            ax.barh(i, lo, height=h, left=0, color=C_SAVINGS, alpha=0.90, edgecolor="white")
            ax.text(lo - 5000, i, f"−${abs(lo):,.0f}", va="center",
                    ha="right", fontsize=9, color=C_SAVINGS, fontweight="bold")
        if hi > 1:
            ax.barh(i, hi, height=h, left=0, color=C_EXTRA, alpha=0.90, edgecolor="white")
            ax.text(hi + 5000, i, f"+${abs(hi):,.0f}", va="center",
                    ha="left", fontsize=9, color=C_EXTRA, fontweight="bold")
        ax.text(-12_000, i, label, va="center", ha="right", fontsize=9.5, color=F_NAVY)

    ax.axvline(0, color=F_NAVY, lw=1.5, zorder=5)
    ax.set_yticks(y)
    ax.set_yticklabels([""] * len(entries))
    ax.set_xlabel("Change vs baseline  ($302,535)", fontsize=10)
    ax.set_facecolor("#F5F6FA")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.grid(True, axis="x", alpha=0.5)
    ax.set_xlim(-220_000, 240_000)

    legend_els = [
        mpatches.Patch(color=C_SAVINGS, label="Cost reduction vs baseline"),
        mpatches.Patch(color=C_EXTRA,   label="Cost increase vs baseline"),
    ]
    ax.legend(handles=legend_els, loc="lower right", fontsize=9)
    _title_block(ax,
                 "Part II — One-at-a-time sensitivity tornado",
                 "Baseline = $302,535  ·  Production cost is the dominant driver")
    fig.tight_layout()
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
    sep_positions: list[float] = []
    y = 0.0
    y_positions = []

    for p in param_order:
        for r in groups[p]:
            bar_labels.append(r["value"])
            s1_vals.append(float(r["stage1_cost_usd"]))
            s2_vals.append(float(r["stage2_cost_usd"]))
            totals.append(float(r["total_expected_cost_usd"]))
            y_positions.append(y)
            y += 1.0
        sep_positions.append(y - 0.5)
        y += 0.45  # gap between groups

    fig, ax = plt.subplots(figsize=(11, 9))

    ax.barh(y_positions, s1_vals, height=0.6,
            label="Stage-1 (anticipatory)", color=C_STAGE1, edgecolor="white")
    ax.barh(y_positions, s2_vals, height=0.6, left=s1_vals,
            label="Stage-2 (reactive expected)", color=C_STAGE2, edgecolor="white")

    for yp, tot in zip(y_positions, totals):
        ax.text(tot + 3000, yp, f"${tot:,.0f}", va="center", fontsize=8, color=F_NAVY)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(bar_labels, fontsize=8.5)
    ax.set_xlabel("USD")

    # group labels on the right
    group_y: dict[str, list] = {p: [] for p in param_order}
    for i, p in enumerate(param_order):
        grp_ys = [y_positions[j] for j, r in enumerate(
            [r for r in rows if r["parameter"] in param_order]
        ) if [r for r in rows if r["parameter"] in param_order][j]["parameter"] == p]

    # simpler: recompute per group
    idx = 0
    for p in param_order:
        n = len(groups[p])
        ys_grp = y_positions[idx: idx + n]
        mid = (ys_grp[0] + ys_grp[-1]) / 2
        ax.text(ax.get_xlim()[0] - 60_000 if ax.get_xlim()[0] > 0 else -80_000,
                mid, friendly_param[p],
                ha="right", va="center", fontsize=9, color=F_NAVY, fontweight="bold")
        idx += n

    _clean_ax(ax, "x")
    ax.set_xlim(0, max(totals) * 1.22)
    ax.legend(loc="lower right", fontsize=9)
    _title_block(ax,
                 "Part II — Stage-1 / Stage-2 split by parameter variant",
                 "Purple = anticipatory cost (pre-positioned)  ·  Blue = reactive expected cost")
    fig.tight_layout()
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

    fig, ax = plt.subplots(figsize=(8, 5))

    ax.plot(x_vals, totals,  "o-",  color=F_NAVY,    lw=2.2, ms=9,
            markerfacecolor=F_NAVY,  markeredgecolor="white", markeredgewidth=1.5,
            label="Total expected cost", zorder=4)
    ax.plot(x_vals, s1_vals, "s--", color=C_STAGE1,  lw=1.8, ms=8,
            markerfacecolor=C_STAGE1, markeredgecolor="white", markeredgewidth=1.2,
            label="Stage-1 (anticipatory)", zorder=3)
    ax.plot(x_vals, s2_vals, "^--", color=C_STAGE2,  lw=1.8, ms=8,
            markerfacecolor=C_STAGE2, markeredgecolor="white", markeredgewidth=1.2,
            label="Stage-2 (reactive)", zorder=3)

    for xv, tot in zip(x_vals, totals):
        ax.annotate(f"${tot/1e3:.0f}k", (xv, tot),
                    textcoords="offset points", xytext=(0, 10),
                    ha="center", fontsize=9, fontweight="bold", color=F_NAVY)

    # slope annotation
    if len(x_vals) >= 2:
        slope = (totals[-1] - totals[0]) / (x_vals[-1] - x_vals[0])
        mid_x = x_vals[1]
        mid_y = totals[1]
        ax.annotate(
            f"slope ≈ ${slope:,.0f} / $1 per m²",
            xy=(mid_x, mid_y),
            xytext=(mid_x + 10, mid_y - 80_000),
            arrowprops={"arrowstyle": "->", "color": C_NEUTRAL, "lw": 1.2},
            fontsize=9, color=F_NAVY,
        )

    ax.set_xlabel("Production cost (USD / m²)", fontsize=10)
    ax.set_ylabel("Expected cost (USD)", fontsize=10)
    ax.set_xticks(x_vals)
    ax.set_xticklabels([f"${int(v)}/m²" for v in x_vals], fontsize=10)
    _clean_ax(ax, "y")
    ax.legend(loc="upper left", fontsize=9)
    _title_block(ax,
                 "Part II — Sensitivity to production cost per m²",
                 "Linear relationship: every $1/m² shifts total expected cost by ~$3,600")
    fig.tight_layout()
    _save(fig, "part2_prod_cost_curve.png")


def fig_anticipatory_by_match():
    r = solve_stochastic(verbose=False)

    forced_set = set(r["forced_anticipatory_matches"])
    match_ids  = sorted(r["match_venue"].keys())
    venues     = [r["match_venue"].get(mid, "?").replace("STAD_", "") for mid in match_ids]
    windows    = [r["match_window"].get(mid, 0) for mid in match_ids]
    vol        = r["vol_per_match_m3"]

    colors = [C_FORCED if mid in forced_set else C_REACTIVE for mid in match_ids]

    fig, ax = plt.subplots(figsize=(13, 5))
    x = np.arange(len(match_ids))

    bars = ax.bar(x, [vol] * len(match_ids),
                  color=colors, edgecolor="white", linewidth=0.6,
                  width=0.62, alpha=0.92)

    # window annotation above each bar
    for i, (win, mid) in enumerate(zip(windows, match_ids)):
        forced = mid in forced_set
        ax.text(i, vol + 0.004,
                f"w={win}d",
                ha="center", va="bottom", fontsize=7.5,
                color=C_FORCED if forced else F_NAVY,
                fontweight="bold" if forced else "normal",
                rotation=40)

    ax.set_xticks(x)
    ax.set_xticklabels(
        [f"M{mid}\n{v}" for mid, v in zip(match_ids, venues)],
        fontsize=8
    )
    ax.set_ylabel("Nominative volume per match (m³)")
    ax.set_ylim(0, vol * 3.0)
    _clean_ax(ax, "y")

    legend_els = [
        mpatches.Patch(color=C_FORCED,   label=f"Forced anticipatory — {len(forced_set)} matches "
                                               f"(window ≤ transit + 1 day)"),
        mpatches.Patch(color=C_REACTIVE, label=f"Reactive — {len(match_ids)-len(forced_set)} matches "
                                               f"(served after draw)"),
    ]
    ax.legend(handles=legend_els, loc="upper right", fontsize=9)
    _title_block(ax,
                 "Part II — Supply strategy by R32 match",
                 "Red = forced anticipatory  ·  Green = reactive  ·  w = window days from GSE")
    fig.tight_layout()
    _save(fig, "part2_anticipatory_by_match.png")


# ============================================================================
# Entry point
# ============================================================================

def main():
    print("Generating Part I figures...")
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

    print("Generating Part II figures...")
    fig_part2_stage_split()
    fig_part2_feasibility()
    fig_part2_sensitivity_tornado()
    fig_part2_stage_by_param()
    fig_part2_prod_cost_curve()
    fig_anticipatory_by_match()

    print(f"\nAll 16 figures written to {dl.FIGURES_DIR}")


if __name__ == "__main__":
    main()
