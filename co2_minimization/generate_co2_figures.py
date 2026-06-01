"""
Generate CO₂-section figures (soft cargo only, LED excluded).
Saves to: ~/Desktop/Logistics_Report/figures/
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

OUT_DIR = Path.home() / "Desktop" / "Logistics_Report" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
C1 = "#375AFE"   # bright blue
C2 = "#8DBAFE"   # light blue
C3 = "#1A2688"   # dark navy
C4 = "#000000"   # black
C5 = "#C9B488"   # lighter gold
C6 = "#7A6438"   # darker gold
GRAY = "#D1D4D1"

plt.rcParams.update({
    "font.family":     "serif",
    "font.serif":      ["Palatino", "Palatino Linotype", "Georgia", "DejaVu Serif"],
    "font.size":       11,
    "axes.titlesize":  12,
    "axes.labelsize":  11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

# ── Model results (from 03_fcl_co2.py and 04_lcl_co2.py, soft only) ──────────
#
# FCL CO₂-opt: D01=6 FEUs, D02=6, D04=5, D05=13 → 30 FEUs, 228.6 t
# LCL CO₂-opt: D01=325 m³, D02=333, D04=272, D05=724 → 225.0 t
#
# Emission factors (GLEC v3 / ISO 14083)
RHO_SOFT   = 0.460   # t/m³
EPS_SHIP   = 16.0    # g CO₂ / tonne-km
EPS_TRUCK  = 1.0     # kg CO₂ / km
FEU_PAY    = 26.0    # t / FEU (weight-limited)

SEA_DIST = {
    "D01": 10_200, "D02": 21_100, "D03": 22_200,
    "D04":  8_500, "D05": 10_900, "D06": 19_500,
}
PORT_LABELS = {
    "D01": "Los Angeles\n(10,200 km)",
    "D02": "New York\n(21,100 km)",
    "D03": "Houston\n(22,200 km)",
    "D04": "Vancouver\n(8,500 km)",
    "D05": "Manzanillo\n(10,900 km)",
    "D06": "Veracruz\n(19,500 km)",
}

USED_PORTS = {"D01", "D02", "D04", "D05"}   # optimal solution

# ── Ocean CO₂ per m³ soft cargo, per port ─────────────────────────────────────
CO2_PER_M3 = {d: EPS_SHIP * RHO_SOFT * SEA_DIST[d] / 1000 for d in SEA_DIST}

# FCL breakdown: ocean + truck (total = 228.6 t)
FCL_FEU = {"D01": 6, "D02": 6, "D04": 5, "D05": 13}
fcl_ocean_t = sum(
    FCL_FEU[d] * EPS_SHIP * FEU_PAY * SEA_DIST[d] / 1e6
    for d in FCL_FEU
)   # 154.7 t
fcl_total_t  = 228.6
fcl_truck_t  = fcl_total_t - fcl_ocean_t   # 73.9 t

# LCL breakdown: ocean + truck (total = 225.0 t)
LCL_VOL = {"D01": 325, "D02": 333, "D04": 272, "D05": 724}
lcl_ocean_t = sum(
    LCL_VOL[d] * EPS_SHIP * RHO_SOFT * SEA_DIST[d] / 1e6
    for d in LCL_VOL
)   # 151.2 t
lcl_total_t  = 225.0
lcl_truck_t  = lcl_total_t - lcl_ocean_t   # 73.8 t


# ─────────────────────────────────────────────────────────────────────────────
# 1. co2_port_efficiency.png — Ocean CO₂ per m³ by port
# ─────────────────────────────────────────────────────────────────────────────
order  = sorted(SEA_DIST, key=lambda d: CO2_PER_M3[d])   # ascending
values = [CO2_PER_M3[d] for d in order]
labels = [PORT_LABELS[d] for d in order]
colors = [C1 if d in USED_PORTS else C4 for d in order]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(labels, values, color=colors, height=0.55)

for bar, val, d in zip(bars, values, order):
    suffix = "" if d in USED_PORTS else "  (excl.)"
    ax.text(val + 0.8, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f} kg/m³{suffix}", va="center", fontsize=9,
            color="black" if d in USED_PORTS else "#555555")

ax.set_xlabel("Ocean CO₂ per m³ of soft cargo (kg)")
ax.set_title("Port emission efficiency — soft cargo ocean leg\n"
             "(16 g CO₂/tonne-km × 0.46 t/m³ × sea distance)")
ax.set_xlim(0, 215)

used_patch     = mpatches.Patch(color=C1, label="Selected (4 ports)")
excluded_patch = mpatches.Patch(color=C4, label="Excluded (Houston, Veracruz)")
ax.legend(handles=[used_patch, excluded_patch], frameon=False, loc="lower right")

plt.tight_layout()
plt.savefig(OUT_DIR / "co2_port_efficiency.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved co2_port_efficiency.png")


# ─────────────────────────────────────────────────────────────────────────────
# 2. co2_breakdown.png — FCL vs LCL CO₂-opt: ocean + truck stack
# ─────────────────────────────────────────────────────────────────────────────
labels2   = ["FCL CO₂-optimal\n(LA + NY + VAN + MNZ)", "LCL CO₂-optimal\n(LA + NY + VAN + MNZ)"]
ocean_t   = [round(fcl_ocean_t, 1), round(lcl_ocean_t, 1)]
truck_t   = [round(fcl_truck_t, 1), round(lcl_truck_t, 1)]
totals_t  = [fcl_total_t, lcl_total_t]

fig, ax = plt.subplots(figsize=(7, 5))
x = np.arange(len(labels2))
w = 0.45

ax.bar(x, ocean_t, width=w, label="Ocean CO₂", color=C1)
ax.bar(x, truck_t, width=w, bottom=ocean_t, label="Truck CO₂", color=C2)

for i, (tot, oc, tr) in enumerate(zip(totals_t, ocean_t, truck_t)):
    ax.text(i, tot + 2, f"{tot:.1f} t", ha="center", fontsize=11, fontweight="bold")

# annotate ocean / truck split
for i, (oc, tr) in enumerate(zip(ocean_t, truck_t)):
    ax.text(i, oc / 2, f"{oc:.1f} t\n({oc/totals_t[i]*100:.0f}%)",
            ha="center", va="center", fontsize=9, color="white", fontweight="bold")
    ax.text(i, oc + tr / 2, f"{tr:.1f} t\n({tr/totals_t[i]*100:.0f}%)",
            ha="center", va="center", fontsize=9, color="black")

ax.set_xticks(x)
ax.set_xticklabels(labels2)
ax.set_ylabel("CO₂ emissions (tonnes)")
ax.set_ylim(0, 270)
ax.set_title("CO₂-optimal scenarios: ocean vs truck breakdown\n(soft cargo only — LED rented locally)")
ax.legend(frameon=False, loc="upper right")
plt.tight_layout()
plt.savefig(OUT_DIR / "co2_breakdown.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved co2_breakdown.png")


# ─────────────────────────────────────────────────────────────────────────────
# 3. co2_sensitivity.png — OAT sensitivity on FCL CO₂-optimal (228.6 t)
# ─────────────────────────────────────────────────────────────────────────────
BASELINE = 228.6   # tonnes

# ±20% effect on total CO₂ (derived from model structure):
#   Sea dist ±20% → FEUs × 16 × 26 × Δdist / 1e6
#   Truck dist ±20% → Δ(truck component)
PARAMS_CO2 = [
    "Sea dist. Manzanillo",
    "Sea dist. New York",
    "Truck dist. USA",
    "Sea dist. Los Angeles",
    "Truck dist. Mexico",
    "Sea dist. Vancouver",
]
# ± tonnes CO₂
DELTAS_CO2 = [11.8, 10.5, 9.8, 5.1, 4.1, 3.5]

fig, ax = plt.subplots(figsize=(9, 4.5))
y_pos = np.arange(len(PARAMS_CO2))
ax.barh(y_pos, [-d for d in DELTAS_CO2], align="center", color=C1, label="−20%")
ax.barh(y_pos, DELTAS_CO2,               align="center", color=C2, label="+20%")
ax.set_yticks(y_pos)
ax.set_yticklabels(PARAMS_CO2)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Change in total CO₂ (tonnes)")
ax.set_title(f"OAT sensitivity — FCL CO₂-optimal (baseline {BASELINE} t, ±20% each parameter)")
ax.legend(frameon=False)
plt.tight_layout()
plt.savefig(OUT_DIR / "co2_sensitivity.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved co2_sensitivity.png")

# ─────────────────────────────────────────────────────────────────────────────
# 4. co2_vs_cost.png — cost-optimal vs CO₂-optimal comparison (soft only)
# ─────────────────────────────────────────────────────────────────────────────
# FCL cost-opt (soft only): $262,240 / 277.9 t  →  LA+NY+HOU+VAN
# FCL CO₂-opt  (soft only): $300,043 / 228.6 t  →  LA+NY+VAN+MNZ
COST_OPT_COST  = 262_240
CO2_OPT_COST   = 300_043
COST_OPT_CO2   = 277.9
CO2_OPT_CO2    = 228.6
SHADOW_PRICE   = (CO2_OPT_COST - COST_OPT_COST) / (COST_OPT_CO2 - CO2_OPT_CO2)  # $/t

labels_comp = ["FCL cost-optimal\n(LA+NY+HOU+VAN)", "FCL CO₂-optimal\n(LA+NY+VAN+MNZ)"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

# Left: cost
bars1 = ax1.bar([0, 1], [COST_OPT_COST/1000, CO2_OPT_COST/1000],
                width=0.5, color=[C1, C2])
ax1.set_xticks([0, 1])
ax1.set_xticklabels(labels_comp)
ax1.set_ylabel("Total logistics cost ($K)")
ax1.set_title("Total cost (soft cargo only)")
ax1.set_ylim(0, 360)
for bar, v in zip(bars1, [COST_OPT_COST, CO2_OPT_COST]):
    ax1.text(bar.get_x() + bar.get_width()/2, v/1000 + 4,
             f"${v/1000:.0f}K", ha="center", fontsize=10, fontweight="bold")
ax1.text(1.27, (COST_OPT_COST + CO2_OPT_COST)/2/1000,
         f"+${(CO2_OPT_COST-COST_OPT_COST)/1000:.0f}K\n(+{(CO2_OPT_COST-COST_OPT_COST)/COST_OPT_COST*100:.0f}%)",
         va="center", fontsize=9, color=C3)

# Right: CO₂
bars2 = ax2.bar([0, 1], [COST_OPT_CO2, CO2_OPT_CO2],
                width=0.5, color=[C1, C2])
ax2.set_xticks([0, 1])
ax2.set_xticklabels(labels_comp)
ax2.set_ylabel("Total CO₂ (tonnes)")
ax2.set_title("Total CO₂ emissions (soft cargo only)")
ax2.set_ylim(0, 330)
for bar, v in zip(bars2, [COST_OPT_CO2, CO2_OPT_CO2]):
    ax2.text(bar.get_x() + bar.get_width()/2, v + 3,
             f"{v:.1f} t", ha="center", fontsize=10, fontweight="bold")
ax2.text(1.27, (COST_OPT_CO2 + CO2_OPT_CO2)/2,
         f"-{COST_OPT_CO2-CO2_OPT_CO2:.1f} t\n(-{(COST_OPT_CO2-CO2_OPT_CO2)/COST_OPT_CO2*100:.0f}%)",
         va="center", fontsize=9, color=C3)

fig.suptitle(f"Cost vs CO₂ trade-off — shadow carbon price: ${SHADOW_PRICE:.0f}/t CO₂",
             fontsize=12, y=1.01)
plt.tight_layout()
plt.savefig(OUT_DIR / "co2_vs_cost.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved co2_vs_cost.png")

print(f"\nAll CO₂ figures saved to {OUT_DIR}")
