"""
Visualisations (guideline p.3/p.6: "give graphical representations").

Produces, in outputs/figures/:

  --- Part I (deterministic LRP) ---
  * part1_network_map.png          geographic map: China->ports->depots->stadiums
  * part1_cost_breakdown.png       stacked bar of Part I cost components
  * part1_feu_by_class.png         LED vs SOFT FEU, weight-on vs weight-off
  * part1_port_utilization.png     FEU allocation per port × class
  * part1_stadium_demand.png       per-stadium demand sorted by total volume
  * part1_demand_heatmap.png       heatmap: stadiums × postes, colour = volume
  * part1_setup_comparison.png     4 setup configs: cost + FEU dual-axis
  * part1_sensitivity_tornado.png  tornado chart: OAT cost sensitivity
  * part1_flow_matrix.png          heatmap: depot × stadium soft-goods volumes
  * part1_cost_donut.png           donut chart of cost component shares

  --- Part II (two-stage stochastic) ---
  * part2_stage_split.png              anticipatory vs reactive cost split
  * part2_feasibility.png             per-match window vs min transit
  * part2_sensitivity_tornado.png     tornado chart: Part II OAT sensitivity
  * part2_stage_by_param.png          stage-1/2 split per parameter variant
  * part2_prod_cost_curve.png         production cost sensitivity (3 lines)
  * part2_anticipatory_by_match.png   forced vs reactive per R32 match

Uses matplotlib only (no internet, no basemap) — coastlines are approximated
by plotting node lat/lon directly, which is enough to read the network.
"""
from __future__ import annotations

import csv
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import matplotlib.colors as mcolors     # noqa: E402
import numpy as np                       # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from common import data_loader as dl    # noqa: E402
from part1_lrp.model import solve_lrp  # noqa: E402
from part2_stochastic.model import solve_stochastic  # noqa: E402


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _node_coords():
    rows = []
    with open(os.path.join(dl.RAW_DIR, "nodes.csv"), encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    return {r["node_id"]: (float(r["latitude"]), float(r["longitude"]),
                           r["node_type"], r["node_name"]) for r in rows}


def _load_json(name: str) -> dict:
    path = os.path.join(dl.RESULTS_DIR, name)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _read_results_csv(name: str) -> list[dict]:
    path = os.path.join(dl.RESULTS_DIR, name)
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _save(fig, name: str):
    os.makedirs(dl.FIGURES_DIR, exist_ok=True)
    path = os.path.join(dl.FIGURES_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path}")


# ---------------------------------------------------------------------------
# Part I – original figures (preserved)
# ---------------------------------------------------------------------------

def fig_network_map():
    coords = _node_coords()
    r = solve_lrp(verbose=False)
    fig, ax = plt.subplots(figsize=(11, 7))

    styles = {"stadium": ("o", "#1f77b4", 40), "candidate_depot": ("s", "#ff7f0e", 90),
              "port_gateway": ("^", "#2ca02c", 120), "production_site": ("D", "#888", 30)}
    for nid, (lat, lon, ntype, name) in coords.items():
        if ntype in styles and "CHINA" not in nid:
            m, c, s = styles[ntype]
            faint = 0.25 if ntype == "production_site" else 1.0
            ax.scatter(lon, lat, marker=m, c=c, s=s, alpha=faint, zorder=3,
                       edgecolors="k", linewidths=0.3)

    for (d, s), v in r["flows_soft_ds"].items():
        if d in coords and s in coords:
            ax.plot([coords[d][1], coords[s][1]], [coords[d][0], coords[s][0]],
                    color="#999", lw=0.6 + 2.0 * v / 120, alpha=0.5, zorder=2)
    for (p, s), v in r["flows_led_ps"].items():
        if p in coords and s in coords:
            ax.plot([coords[p][1], coords[s][1]], [coords[p][0], coords[s][0]],
                    color="#2ca02c", lw=0.6 + 2.0 * v / 67, alpha=0.4,
                    ls="--", zorder=1)

    for p in r["ports_open"]:
        lat, lon = coords[p][0], coords[p][1]
        ax.scatter(lon, lat, marker="^", c="#2ca02c", s=260, edgecolors="k",
                   linewidths=1.2, zorder=5)
    for d in r["depots_open"]:
        lat, lon = coords[d][0], coords[d][1]
        ax.scatter(lon, lat, marker="s", c="#ff7f0e", s=200, edgecolors="k",
                   linewidths=1.2, zorder=5)

    ax.set_title(f"Part I optimal network — ${r['total_cost']:,.0f}  "
                 f"({r['feu_total']:.0f} FEU)\n"
                 "green ▲ = open port (LED direct dashed), orange ■ = open depot "
                 "(soft goods grey), blue ● = stadium")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
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
        ax.bar("Part I", v, bottom=bottom, label=f"{lab}  (${v:,.0f})",
               color=colors[i % 10])
        bottom += v
    ax.set_ylabel("USD")
    ax.set_title(f"Part I cost breakdown — total ${r['total_cost']:,.0f}")
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
    ax.set_title("The LED weight effect: 26 t ceiling forces more containers\n"
                 f"${on['total_cost']:,.0f} vs ${off['total_cost']:,.0f}")
    ax.legend()
    _save(fig, "part1_feu_by_class.png")


# ---------------------------------------------------------------------------
# Part I – new figures
# ---------------------------------------------------------------------------

def fig_port_utilization():
    """Grouped bar: FEU by port and class (LED / soft), with LCL annotation."""
    s = _load_json("part1_summary.json")
    ports_data = s["ports_open"]

    short_names = {
        "PORT_LA_LB": "LA / Long Beach",
        "PORT_NY_NJ": "New York / NJ",
        "PORT_VAN":   "Vancouver",
    }
    port_order = list(ports_data.keys())
    labels = [short_names.get(p, p) for p in port_order]
    feu_led  = [ports_data[p]["feu_led"]  for p in port_order]
    feu_soft = [ports_data[p]["feu_soft"] for p in port_order]
    lcl_vals = [ports_data[p]["lcl_soft"] for p in port_order]

    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(8, 5))
    bars_led  = ax.bar(x - w / 2, feu_led,  w, label="LED FEU",  color="#1f77b4")
    bars_soft = ax.bar(x + w / 2, feu_soft, w, label="Soft FEU", color="#ff7f0e")

    # annotate FEU counts above bars
    for bar in bars_led:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3,
                    f"{int(h)}", ha="center", va="bottom", fontsize=9)
    for bar in bars_soft:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3,
                    f"{int(h)}", ha="center", va="bottom", fontsize=9)

    # annotate LCL volume below x-axis labels
    for i, lcl in enumerate(lcl_vals):
        if lcl > 0:
            ax.annotate(f"+ {lcl:.1f} m³ LCL", xy=(x[i], -1.5),
                        ha="center", fontsize=8, color="#555", style="italic")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("FEU (40ft containers)")
    ax.set_title("Part I — Port utilisation by material class\n"
                 f"Total: {int(s['feu_led_total'])} LED + {int(s['feu_soft_total'])} soft"
                 f" = {int(s['feu_total'])} FEU")
    ax.legend()
    ax.set_ylim(bottom=-3)
    ax.grid(axis="y", alpha=0.3)
    _save(fig, "part1_port_utilization.png")


def fig_stadium_demand():
    """Horizontal stacked bar: LED + soft volume per stadium, sorted by total."""
    path = os.path.join(dl.GENERATED_DIR, "stadium_demand_by_class.csv")
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    rows.sort(key=lambda r: float(r["vol_total_m3"]), reverse=True)
    stads  = [r["stadium_id"] for r in rows]
    v_led  = [float(r["vol_led_m3"])  for r in rows]
    v_soft = [float(r["vol_soft_m3"]) for r in rows]
    v_tot  = [float(r["vol_total_m3"]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 7))
    y = np.arange(len(stads))
    ax.barh(y, v_led,  height=0.6, label="LED perimeter (constant 67 m³)",
            color="#7f7f7f")
    ax.barh(y, v_soft, height=0.6, left=v_led, label="Soft goods (variable)",
            color="#2ca02c")

    for i, (tot, vl) in enumerate(zip(v_tot, v_led)):
        ax.text(tot + 1.5, i, f"{tot:.0f} m³", va="center", fontsize=8)

    ax.set_yticks(y)
    ax.set_yticklabels(stads, fontsize=9)
    ax.set_xlabel("Volume (m³)")
    ax.set_title("Part I — Stadium demand by material class\n"
                 "Sorted by total volume (LED is identical at every venue; soft goods vary)")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    _save(fig, "part1_stadium_demand.png")


def fig_demand_by_poste():
    """Heatmap: stadiums × postes, colour = volume (m³)."""
    path = os.path.join(dl.GENERATED_DIR, "stadium_demand_by_poste.csv")
    with open(path, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    # build pivot
    stads  = sorted({r["stadium_id"] for r in rows})
    postes = sorted({r["poste"] for r in rows})

    # order postes by total volume descending
    poste_totals = {p: sum(float(r["volume_m3"]) for r in rows if r["poste"] == p)
                    for p in postes}
    postes = sorted(postes, key=lambda p: poste_totals[p], reverse=True)

    # order stadiums by total volume descending
    stad_totals = {s: sum(float(r["volume_m3"]) for r in rows if r["stadium_id"] == s)
                   for s in stads}
    stads = sorted(stads, key=lambda s: stad_totals[s], reverse=True)

    lookup = {(r["stadium_id"], r["poste"]): float(r["volume_m3"]) for r in rows}
    matrix = np.array([[lookup.get((s, p), 0.0) for p in postes] for s in stads])

    fig, ax = plt.subplots(figsize=(13, 8))
    im = ax.imshow(matrix, cmap="Blues", aspect="auto")

    ax.set_xticks(range(len(postes)))
    ax.set_xticklabels(postes, rotation=35, ha="right", fontsize=8)
    ax.set_yticks(range(len(stads)))
    ax.set_yticklabels(stads, fontsize=8)

    # annotate cells
    for i in range(len(stads)):
        for j in range(len(postes)):
            v = matrix[i, j]
            txt_col = "white" if v > matrix.max() * 0.55 else "black"
            ax.text(j, i, f"{v:.1f}", ha="center", va="center",
                    fontsize=6.5, color=txt_col)

    plt.colorbar(im, ax=ax, label="Volume (m³)")
    ax.set_title("Part I — Demand heatmap: stadium × equipment type (poste)\n"
                 "Postes and stadiums sorted by total volume (descending)")
    _save(fig, "part1_demand_heatmap.png")


def fig_setup_comparison():
    """Dual-axis bar+line: cost (left y) and FEU (right y) across 4 setups."""
    rows = _read_results_csv("part1_setup_comparison.csv")

    # Shorten setup labels
    short = {
        "Baseline (LED direct, depots, weight, LCL)": "Baseline",
        "LED via depot (no direct)": "LED via\ndepot",
        "Volume-only (no weight constraint)": "Volume\nonly",
        "FCL-only (no LCL)": "FCL\nonly",
    }
    labels   = [short.get(r["setup"], r["setup"]) for r in rows]
    costs    = [float(r["total_cost_usd"]) for r in rows]
    feu_tots = [float(r["feu_total"])      for r in rows]
    baseline_cost = costs[0]

    x = np.arange(len(labels))
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # colour bars: green if cheaper than baseline, red if more expensive
    bar_colors = []
    for c in costs:
        if c < baseline_cost - 1:
            bar_colors.append("#2ca02c")
        elif c > baseline_cost + 1:
            bar_colors.append("#d62728")
        else:
            bar_colors.append("#1f77b4")

    bars = ax1.bar(x, costs, color=bar_colors, alpha=0.85, width=0.5, label="Total cost (USD)")
    ax1.set_ylabel("Total cost (USD)", color="#1f77b4")
    ax1.tick_params(axis="y", labelcolor="#1f77b4")
    ax1.set_ylim(0, max(costs) * 1.18)

    # annotate delta vs baseline
    for i, (bar, c) in enumerate(zip(bars, costs)):
        delta = c - baseline_cost
        sign  = "+" if delta >= 0 else ""
        label = f"${c:,.0f}\n({sign}{delta:,.0f})" if i > 0 else f"${c:,.0f}\n(baseline)"
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + max(costs) * 0.01,
                 label, ha="center", va="bottom", fontsize=8, color="k")

    # FEU as a line on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(x, feu_tots, "D--", color="#ff7f0e", lw=2, ms=9, label="Total FEU")
    for i, f in enumerate(feu_tots):
        ax2.text(i, f + 0.8, f"{int(f)} FEU", ha="center", color="#ff7f0e", fontsize=8)
    ax2.set_ylabel("Total FEU (40ft containers)", color="#ff7f0e")
    ax2.tick_params(axis="y", labelcolor="#ff7f0e")
    ax2.set_ylim(0, max(feu_tots) * 1.25)

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=9)
    ax1.set_title("Part I — Setup comparison: cost & FEU across 4 configurations\n"
                  "Green = saves vs baseline   Red = costs more   Blue = baseline")
    # combined legend
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="upper right")
    ax1.grid(axis="y", alpha=0.3)
    _save(fig, "part1_setup_comparison.png")


def fig_part1_sensitivity_tornado():
    """Horizontal tornado chart: OAT cost sensitivity around the Part I baseline."""
    rows = _read_results_csv("part1_sensitivity.csv")
    baseline = 458_626.0  # from part1_summary.json

    # group by parameter → collect {value: cost}
    params: dict[str, list[tuple[str, float]]] = {}
    for r in rows:
        p = r["parameter"]
        c = float(r["total_cost_usd"])
        params.setdefault(p, []).append((r["value"], c))

    # compute low/high deviation from baseline for each parameter
    entries = []
    for param, vals in params.items():
        costs = [c for _, c in vals]
        lo = min(costs) - baseline   # negative or 0
        hi = max(costs) - baseline   # positive or 0
        entries.append((param, lo, hi, min(costs), max(costs)))

    # sort by absolute total swing (largest first)
    entries.sort(key=lambda e: abs(e[1]) + abs(e[2]), reverse=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    y = np.arange(len(entries))
    h = 0.45

    friendly = {
        "weight_constraint":  "Weight constraint\n(on / off)",
        "led_routing":        "LED routing\n(direct / via depot)",
        "lcl_policy":         "LCL policy\n(allowed / FCL-only)",
    }

    for i, (param, lo, hi, clo, chi) in enumerate(entries):
        label = friendly.get(param, param)
        if lo < 0:
            ax.barh(i, lo, height=h, left=0, color="#2ca02c", alpha=0.85)
            ax.text(lo - 2000, i, f"−${abs(lo):,.0f}", va="center",
                    ha="right", fontsize=8, color="#2ca02c")
        if hi > 0:
            ax.barh(i, hi, height=h, left=0, color="#d62728", alpha=0.85)
            ax.text(hi + 2000, i, f"+${abs(hi):,.0f}", va="center",
                    ha="left", fontsize=8, color="#d62728")
        ax.text(-5000, i, label, va="center", ha="right", fontsize=9)

    ax.axvline(0, color="k", lw=1.2)
    ax.set_yticks(y)
    ax.set_yticklabels([""] * len(entries))  # labels drawn manually above
    ax.set_xlabel("Change vs baseline ($458,626)")
    ax.set_title("Part I — OAT sensitivity tornado\n"
                 "Green = cost reduction   Red = cost increase   Baseline = $458,626")
    ax.grid(axis="x", alpha=0.3)
    ax.set_xlim(-160_000, 20_000)
    _save(fig, "part1_sensitivity_tornado.png")


def fig_soft_flow_matrix():
    """Heatmap: depot × stadium, colour = soft-goods volume shipped (m³)."""
    rows = _read_results_csv("part1_flows_soft.csv")

    # west-to-east stadium order (rough longitude order)
    stad_order = ["STAD_SF", "STAD_SEA", "STAD_VAN", "STAD_LA",
                  "STAD_GDL", "STAD_MTY", "STAD_MEX",
                  "STAD_DAL", "STAD_HOU",
                  "STAD_KC", "STAD_ATL",
                  "STAD_MIA", "STAD_TOR",
                  "STAD_NY_NJ", "STAD_PHI", "STAD_BOS"]
    short_stad = {s: s.replace("STAD_", "") for s in stad_order}

    depot_order = ["LAX_DEPOT_NODE", "EWR_DEPOT_NODE"]
    short_depot = {"LAX_DEPOT_NODE": "LAX depot", "EWR_DEPOT_NODE": "EWR depot"}

    lookup = {(r["depot_node"], r["stadium_node"]): float(r["volume_m3"]) for r in rows}
    stads_present = {r["stadium_node"] for r in rows}
    stads_used = [s for s in stad_order if s in stads_present]

    matrix = np.array(
        [[lookup.get((d, s), 0.0) for s in stads_used] for d in depot_order]
    )

    fig, ax = plt.subplots(figsize=(14, 3.5))
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "wh_bl", ["#ffffff", "#08306b"])
    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=0)

    ax.set_xticks(range(len(stads_used)))
    ax.set_xticklabels([short_stad[s] for s in stads_used], rotation=35, ha="right", fontsize=8)
    ax.set_yticks(range(len(depot_order)))
    ax.set_yticklabels([short_depot[d] for d in depot_order], fontsize=9)

    for i in range(len(depot_order)):
        for j in range(len(stads_used)):
            v = matrix[i, j]
            if v > 0:
                txt_col = "white" if v > matrix.max() * 0.6 else "black"
                ax.text(j, i, f"{v:.0f}", ha="center", va="center",
                        fontsize=8, color=txt_col, fontweight="bold")
            else:
                ax.text(j, i, "—", ha="center", va="center", fontsize=8, color="#bbb")

    plt.colorbar(im, ax=ax, label="Volume shipped (m³)", shrink=0.8)
    ax.set_title("Part I — Soft-goods flow matrix (depot → stadium)\n"
                 "LAX serves West/Central   ·   EWR serves East   ·   ordered West → East")
    _save(fig, "part1_flow_matrix.png")


def fig_cost_donut():
    """Donut chart: Part I cost component shares."""
    s = _load_json("part1_summary.json")
    cb = s["cost_breakdown"]
    total = s["total_cost"]

    friendly = {
        "sea":                    "Ocean freight",
        "depot_fixed":            "Depot fixed cost",
        "depot_handling":         "Depot handling",
        "truck_port_depot":       "Trucking port→depot",
        "truck_depot_stadium":    "Trucking depot→stadium",
        "truck_port_stadium_led": "Trucking port→stadium\n(LED direct)",
    }
    labels = [friendly[k] for k in cb]
    sizes  = [cb[k] for k in cb]
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b"]

    fig, ax = plt.subplots(figsize=(9, 6))
    wedges, texts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        startangle=140,
        wedgeprops={"width": 0.55, "edgecolor": "white", "linewidth": 1.5},
    )

    # pct labels inside wedges
    for wedge, v in zip(wedges, sizes):
        pct = 100.0 * v / total
        if pct >= 3.0:
            angle = (wedge.theta1 + wedge.theta2) / 2
            x = 0.65 * np.cos(np.radians(angle))
            y = 0.65 * np.sin(np.radians(angle))
            ax.text(x, y, f"{pct:.1f}%", ha="center", va="center",
                    fontsize=9, fontweight="bold", color="white")

    legend_labels = [f"{l}  (${v:,.0f})" for l, v in zip(labels, sizes)]
    ax.legend(wedges, legend_labels, loc="center left",
              bbox_to_anchor=(1.0, 0.5), fontsize=8)
    ax.text(0, 0, f"${total/1e3:.0f}k\ntotal", ha="center", va="center",
            fontsize=12, fontweight="bold")
    ax.set_title("Part I — Cost breakdown by component\n"
                 "Ocean freight dominates at 68 % of total")
    _save(fig, "part1_cost_donut.png")


# ---------------------------------------------------------------------------
# Part II – original figures (preserved)
# ---------------------------------------------------------------------------

def fig_part2_stage_split():
    r = solve_stochastic(verbose=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar("Expected cost", r["stage1_cost"],
           label=f"Stage-1 anticipatory  (${r['stage1_cost']:,.0f})",
           color="#9467bd")
    ax.bar("Expected cost", r["stage2_expected_cost"], bottom=r["stage1_cost"],
           label=f"Stage-2 reactive  (${r['stage2_expected_cost']:,.0f})",
           color="#17becf")
    ax.set_ylabel("USD")
    ax.set_title(f"Part II two-stage cost split — total ${r['total_expected_cost']:,.0f}\n"
                 f"{r['n_forced']} of 16 matches FORCED anticipatory (window too short)")
    ax.legend()
    _save(fig, "part2_stage_split.png")


def fig_part2_feasibility():
    from datetime import date
    road = dl.load_road_edges()
    prod = dl.load_production_sites()
    sites = [n for n in prod if n != "PROD_CHINA_SHANGHAI"]
    GSE = date(2026, 6, 27)
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
        matches.append(int(rr["match"]))
        windows.append(win)
        mintransit.append(min(ts) if ts else None)
    fig, ax = plt.subplots(figsize=(11, 5))
    x = range(len(matches))
    ax.bar([i - 0.2 for i in x], windows, width=0.4, label="window (days)",
           color="#2ca02c")
    ax.bar([i + 0.2 for i in x], mintransit, width=0.4,
           label="min transit (days, best site)", color="#d62728")
    ax.axhline(1, color="k", ls=":", lw=1, label="production = 1 day")
    ax.set_xticks(list(x))
    ax.set_xticklabels(matches, rotation=0, fontsize=7)
    ax.set_xlabel("R32 match")
    ax.set_ylabel("days")
    ax.set_title("Part II feasibility: reactive needs min_transit ≤ window − 1\n"
                 "matches where red + 1 > green must be served anticipatorily")
    ax.legend()
    _save(fig, "part2_feasibility.png")


# ---------------------------------------------------------------------------
# Part II – new figures
# ---------------------------------------------------------------------------

def fig_part2_sensitivity_tornado():
    """Horizontal tornado chart: OAT cost sensitivity around the Part II baseline."""
    rows = _read_results_csv("part2_sensitivity.csv")
    baseline = 302_535.0  # base scenario total expected cost

    params: dict[str, list[tuple[str, float]]] = {}
    for r in rows:
        p = r["parameter"]
        c = float(r["total_expected_cost_usd"])
        params.setdefault(p, []).append((r["value"], c))

    entries = []
    for param, vals in params.items():
        costs = [c for _, c in vals]
        lo = min(costs) - baseline
        hi = max(costs) - baseline
        entries.append((param, lo, hi, min(costs), max(costs)))

    entries.sort(key=lambda e: abs(e[1]) + abs(e[2]), reverse=True)

    friendly = {
        "production_cost_per_m2": "Production cost\n($/m²)",
        "anticipatory_waste":     "Anticipatory waste\n(1× / 2× / 3×)",
        "production_days":        "Production days\n(0d / 1d)",
        "storage_scenario":       "Storage scenario\n(low / base / high)",
    }

    fig, ax = plt.subplots(figsize=(10, 5))
    y = np.arange(len(entries))
    h = 0.45

    for i, (param, lo, hi, clo, chi) in enumerate(entries):
        label = friendly.get(param, param)
        if lo < -1:
            ax.barh(i, lo, height=h, left=0, color="#2ca02c", alpha=0.85)
            ax.text(lo - 3000, i, f"−${abs(lo):,.0f}", va="center",
                    ha="right", fontsize=8, color="#2ca02c")
        if hi > 1:
            ax.barh(i, hi, height=h, left=0, color="#d62728", alpha=0.85)
            ax.text(hi + 3000, i, f"+${abs(hi):,.0f}", va="center",
                    ha="left", fontsize=8, color="#d62728")
        ax.text(-8000, i, label, va="center", ha="right", fontsize=9)

    ax.axvline(0, color="k", lw=1.2)
    ax.set_yticks(y)
    ax.set_yticklabels([""] * len(entries))
    ax.set_xlabel("Change vs baseline ($302,535)")
    ax.set_title("Part II — OAT sensitivity tornado\n"
                 "Green = cost reduction   Red = cost increase   Baseline = $302,535")
    ax.grid(axis="x", alpha=0.3)
    ax.set_xlim(-220_000, 240_000)
    _save(fig, "part2_sensitivity_tornado.png")


def fig_part2_stage_by_param():
    """Grouped stacked horizontal bars: stage-1 + stage-2 for every parameter variant."""
    rows = _read_results_csv("part2_sensitivity.csv")

    friendly_param = {
        "storage_scenario":       "Storage scenario",
        "production_cost_per_m2": "Production cost ($/m²)",
        "anticipatory_waste":     "Anticipatory waste",
        "production_days":        "Production days",
    }
    param_order = ["production_cost_per_m2", "anticipatory_waste",
                   "production_days", "storage_scenario"]

    # group rows
    groups: dict[str, list] = {p: [] for p in param_order}
    for r in rows:
        p = r["parameter"]
        if p in groups:
            groups[p].append(r)

    # build y positions and data
    bar_labels, s1_vals, s2_vals, totals = [], [], [], []
    separators = []  # y positions of gaps between parameter groups
    y = 0
    for p in param_order:
        for r in groups[p]:
            bar_labels.append(f"{friendly_param[p]}\n= {r['value']}")
            s1_vals.append(float(r["stage1_cost_usd"]))
            s2_vals.append(float(r["stage2_cost_usd"]))
            totals.append(float(r["total_expected_cost_usd"]))
            y += 1
        separators.append(y - 0.5)  # gap after this group
        y += 0.3  # spacing

    n = len(bar_labels)
    y_pos = np.arange(n)

    fig, ax = plt.subplots(figsize=(11, 8))
    ax.barh(y_pos, s1_vals, height=0.6, label="Stage-1 (anticipatory)", color="#9467bd")
    ax.barh(y_pos, s2_vals, height=0.6, left=s1_vals,
            label="Stage-2 (reactive expected)", color="#17becf")

    for i, tot in enumerate(totals):
        ax.text(tot + 2000, i, f"${tot:,.0f}", va="center", fontsize=8)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(bar_labels, fontsize=8)
    ax.set_xlabel("USD")
    ax.set_title("Part II — Stage-1 vs Stage-2 cost by parameter variant\n"
                 "Purple = anticipatory (pre-positioned)   Cyan = reactive (after draw)")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    ax.set_xlim(0, max(totals) * 1.18)
    _save(fig, "part2_stage_by_param.png")


def fig_part2_prod_cost_curve():
    """Line chart: production cost $/m² vs total / stage-1 / stage-2 cost."""
    rows = _read_results_csv("part2_sensitivity.csv")
    filtered = [r for r in rows if r["parameter"] == "production_cost_per_m2"]
    filtered.sort(key=lambda r: float(r["total_expected_cost_usd"]))

    # parse x-axis values: "$20" → 20
    x_vals  = [float(r["value"].replace("$", "")) for r in filtered]
    totals  = [float(r["total_expected_cost_usd"]) for r in filtered]
    s1_vals = [float(r["stage1_cost_usd"]) for r in filtered]
    s2_vals = [float(r["stage2_cost_usd"]) for r in filtered]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_vals, totals,  "o-", color="k",       lw=2, ms=8, label="Total expected cost")
    ax.plot(x_vals, s1_vals, "s--", color="#9467bd", lw=1.8, ms=7, label="Stage-1 (anticipatory)")
    ax.plot(x_vals, s2_vals, "^--", color="#17becf", lw=1.8, ms=7, label="Stage-2 (reactive)")

    for xv, tot, s1, s2 in zip(x_vals, totals, s1_vals, s2_vals):
        ax.annotate(f"${tot/1e3:.0f}k", (xv, tot), textcoords="offset points",
                    xytext=(0, 8), ha="center", fontsize=8)
        ax.annotate(f"${s1/1e3:.0f}k", (xv, s1), textcoords="offset points",
                    xytext=(0, -14), ha="center", fontsize=7, color="#9467bd")

    # compute slope for annotation
    if len(x_vals) >= 2:
        slope = (totals[-1] - totals[0]) / (x_vals[-1] - x_vals[0])
        ax.annotate(f"slope ≈ ${slope:,.0f} per $1/m²",
                    xy=(x_vals[1], totals[1]),
                    xytext=(x_vals[1] - 8, totals[1] + 60_000),
                    arrowprops={"arrowstyle": "->", "color": "grey"},
                    fontsize=8, color="grey")

    ax.set_xlabel("Production cost (USD/m²)")
    ax.set_ylabel("Expected cost (USD)")
    ax.set_title("Part II — Sensitivity to production cost per m²\n"
                 "Linear relationship: every $1/m² shifts total cost by ~$3,600")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xticks(x_vals)
    ax.set_xticklabels([f"${int(v)}/m²" for v in x_vals])
    _save(fig, "part2_prod_cost_curve.png")


def fig_anticipatory_by_match():
    """Bar chart: per R32 match — forced anticipatory (red) vs reactive (green)."""
    r = solve_stochastic(verbose=False)

    forced_set = set(r["forced_anticipatory_matches"])
    match_ids  = sorted(r["match_venue"].keys())

    colors  = ["#d62728" if mid in forced_set else "#2ca02c" for mid in match_ids]
    volumes = [r["anticipatory_by_match"].get(mid, 0.0) for mid in match_ids]
    windows = [r["match_window"].get(mid, 0) for mid in match_ids]
    venues  = [r["match_venue"].get(mid, "?").replace("STAD_", "") for mid in match_ids]

    fig, ax = plt.subplots(figsize=(13, 5))
    x = np.arange(len(match_ids))
    bars = ax.bar(x, [r["vol_per_match_m3"]] * len(match_ids),
                  color=colors, alpha=0.85, width=0.6, edgecolor="k", linewidth=0.5)

    # window annotation above bars
    for i, (win, mid) in enumerate(zip(windows, match_ids)):
        label = f"w={win}d"
        ax.text(i, r["vol_per_match_m3"] + 0.005, label,
                ha="center", va="bottom", fontsize=7, rotation=45)

    ax.set_xticks(x)
    ax.set_xticklabels([f"M{mid}\n{v}" for mid, v in zip(match_ids, venues)],
                       fontsize=8, rotation=0)
    ax.set_ylabel("Volume per match (m³)")
    ax.set_ylim(0, r["vol_per_match_m3"] * 2.5)
    ax.set_title("Part II — Anticipatory decision by R32 match\n"
                 "Red = FORCED anticipatory (window ≤ transit + 1 day)   "
                 "Green = reactive after draw   w = window (days)")

    # custom legend
    from matplotlib.patches import Patch
    legend_els = [
        Patch(facecolor="#d62728", label=f"Forced anticipatory ({len(forced_set)} matches)"),
        Patch(facecolor="#2ca02c", label=f"Reactive ({len(match_ids)-len(forced_set)} matches)"),
    ]
    ax.legend(handles=legend_els, loc="upper right")
    ax.grid(axis="y", alpha=0.3)
    _save(fig, "part2_anticipatory_by_match.png")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # Part I – original
    fig_network_map()
    fig_cost_breakdown()
    fig_feu_by_class()
    # Part I – new
    fig_port_utilization()
    fig_stadium_demand()
    fig_demand_by_poste()
    fig_setup_comparison()
    fig_part1_sensitivity_tornado()
    fig_soft_flow_matrix()
    fig_cost_donut()
    # Part II – original
    fig_part2_stage_split()
    fig_part2_feasibility()
    # Part II – new
    fig_part2_sensitivity_tornado()
    fig_part2_stage_by_param()
    fig_part2_prod_cost_curve()
    fig_anticipatory_by_match()


if __name__ == "__main__":
    main()
