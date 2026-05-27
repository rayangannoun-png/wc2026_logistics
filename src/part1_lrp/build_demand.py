"""
Build the per-stadium demand vector for Part I, split into two freight classes.

WHY THIS FILE EXISTS
--------------------
The project CSVs contain the full logistics network (nodes, ports, depots,
edges) but NO per-stadium demand in m3. The README references an
`inventory_template.csv` that is not present in the project. We therefore
build the demand ourselves from the WC2026 inventory reconstruction
(reference/Reconstitution_Inventaire_WC2026.md), category by category.

VENTILATION METHOD (3 keys, validated with the user)
----------------------------------------------------
Different inventory items scale differently with stadium size:
  * CAPACITY key  -> scales with seating capacity (interior, seat covers,
                     building wraps, vehicle wraps). Bigger stadium = more
                     concourses/seats/facade to cover.
  * FIXED key     -> identical per stadium (LED: "1 system = 1 container"
                     fixed at 67 m3/stadium; pitch-side: pitch is 105x68m
                     everywhere; wayfinding precinct; alu totems; masts;
                     fence scrim: precinct perimeter, ~equal per venue).
  * TYPOLOGY key  -> brand scrubbing, using the 3-tier split from inventory
                     section B.3 (8 heavily-branded, 5 recent, 3 MX/CA).

FREIGHT CLASSES (for the multidimensional packing in Part I)
------------------------------------------------------------
  * LED   = poste 'led_perimeter' only (heavy ~1000 kg/m3, weight-driven)
  * SOFT  = everything else (light ~460 kg/m3, volume-driven)

The totals reconcile EXACTLY with the inventory: 2726.0 m3 / 1828.0 t.
"""
from __future__ import annotations

import csv
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
GENERATED_DIR = os.path.join(REPO_ROOT, "data", "generated")

# ---------------------------------------------------------------------------
# Stadium seating capacities (WC2026 inventory, Partie A) keyed by stadium_id
# ---------------------------------------------------------------------------
CAP = {
    "NY_NJ": 82500, "MEX": 72700, "DAL": 87000,  # AT&T: midpoint of 80-94k
    "KC": 76400, "HOU": 71500, "ATL": 71000, "LA": 70000,
    "SF": 69400, "SEA": 69000, "BOS": 68800, "PHI": 69000,
    "MIA": 65300, "GDL": 48000, "MTY": 53500, "VAN": 54500, "TOR": 44300,
}

# stadium_id -> node_id (from stadiums.csv)
NODE_OF = {
    "TOR": "STAD_TOR", "VAN": "STAD_VAN", "MEX": "STAD_MEX", "MTY": "STAD_MTY",
    "GDL": "STAD_GDL", "ATL": "STAD_ATL", "BOS": "STAD_BOS", "DAL": "STAD_DAL",
    "HOU": "STAD_HOU", "KC": "STAD_KC", "LA": "STAD_LA", "MIA": "STAD_MIA",
    "NY_NJ": "STAD_NY_NJ", "PHI": "STAD_PHI", "SF": "STAD_SF", "SEA": "STAD_SEA",
}

TOTAL_CAP = sum(CAP.values())

# ---------------------------------------------------------------------------
# Inventory totals per poste (m3) and weight (t), central scenario (LED in).
# Source: WC2026 inventory, sections B.5 / B.6 (volume) and G.1 / G.2 (weight).
# Tuple: (name, total_m3, ventilation_key, total_weight_t_or_None)
# ---------------------------------------------------------------------------
POSTES = [
    # --- capacity-scaled (soft class) ---
    ("interior",        912, "cap", 464),
    ("seat_covers",      54, "cap", 17),
    ("building_wraps",  160, "cap", 109),
    ("vehicle_wraps",     7, "cap", 5),
    # --- fixed per stadium (soft class, except led) ---
    ("led_perimeter",  1072, "fix", 1066),   # LED CLASS (heavy)
    ("pitch_side",       11, "fix", 7),
    ("wayfinding",        6, "fix", 2),
    ("totems_alu",      140, "fix", None),    # weight from structures pool
    ("masts",            60, "fix", None),    # weight from structures pool
    ("fence_scrim",     236, "fix", 43),
    # --- typology (soft class) ---
    ("brand_scrub",      68, "typ", 35),
]

# alu totems + masts share ~80 t (Partie G), split by volume
STRUCT_T = 80.0
TOTEMS_T = STRUCT_T * 140 / (140 + 60)
MASTS_T = STRUCT_T * 60 / (140 + 60)

# Brand scrubbing per-stadium m2 (inventory B.3, 3 tiers)
SCRUB_M2 = {s: 6000 for s in ["ATL", "KC", "HOU", "DAL", "PHI", "BOS", "MIA", "SEA"]}
SCRUB_M2.update({s: 3000 for s in ["LA", "SF", "NY_NJ"]})
SCRUB_M2.update({s: 2100 for s in ["MEX", "MTY", "GDL", "VAN", "TOR"]})
SCRUB_TOT_M2 = sum(SCRUB_M2.values())

# Which poste belongs to the LED (heavy) class
LED_POSTES = {"led_perimeter"}


def _alloc(total: float, key: str, sid: str) -> float:
    if key == "cap":
        return total * CAP[sid] / TOTAL_CAP
    if key == "fix":
        return total / 16.0
    return 0.0  # typology handled separately


def build_demand() -> list:
    """Return rows: node_id, stadium_id, poste, class, volume_m3, weight_t."""
    rows = []
    for sid in CAP:
        node = NODE_OF[sid]
        for name, tot, key, wt in POSTES:
            cls = "led" if name in LED_POSTES else "soft"
            if name == "brand_scrub":
                v = 68 * SCRUB_M2[sid] / SCRUB_TOT_M2
                w = 35 * SCRUB_M2[sid] / SCRUB_TOT_M2
            elif name == "totems_alu":
                v = _alloc(tot, key, sid)
                w = TOTEMS_T / 16.0
            elif name == "masts":
                v = _alloc(tot, key, sid)
                w = MASTS_T / 16.0
            else:
                v = _alloc(tot, key, sid)
                if key == "cap" and wt:
                    w = wt / TOTAL_CAP * CAP[sid]
                elif wt:
                    w = wt / 16.0
                else:
                    w = 0.0
            rows.append((node, sid, name, cls, round(v, 4), round(w, 4)))
    return rows


def write_outputs(rows: list) -> None:
    os.makedirs(GENERATED_DIR, exist_ok=True)

    # 1) Detailed per-poste file
    detail_path = os.path.join(GENERATED_DIR, "stadium_demand_by_poste.csv")
    with open(detail_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["node_id", "stadium_id", "poste", "class", "volume_m3", "weight_t"])
        w.writerows(rows)

    # 2) Aggregated per-class file (used by the optimisation models)
    agg = {}
    for node, sid, name, cls, v, w in rows:
        d = agg.setdefault(node, dict(sid=sid, vol_led=0.0, wt_led=0.0,
                                      vol_soft=0.0, wt_soft=0.0))
        d[f"vol_{cls}"] += v
        d[f"wt_{cls}"] += w
    class_path = os.path.join(GENERATED_DIR, "stadium_demand_by_class.csv")
    with open(class_path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["node_id", "stadium_id", "vol_led_m3", "wt_led_t",
                    "vol_soft_m3", "wt_soft_t", "vol_total_m3", "wt_total_t"])
        for node, d in agg.items():
            vt = d["vol_led"] + d["vol_soft"]
            wt = d["wt_led"] + d["wt_soft"]
            w.writerow([node, d["sid"], round(d["vol_led"], 4), round(d["wt_led"], 4),
                        round(d["vol_soft"], 4), round(d["wt_soft"], 4),
                        round(vt, 4), round(wt, 4)])
    return detail_path, class_path


def main() -> None:
    rows = build_demand()
    detail_path, class_path = write_outputs(rows)

    # Reconciliation check
    tot_v = sum(r[4] for r in rows)
    tot_w = sum(r[5] for r in rows)
    led_v = sum(r[4] for r in rows if r[3] == "led")
    soft_v = sum(r[4] for r in rows if r[3] == "soft")
    print(f"Wrote {detail_path}")
    print(f"Wrote {class_path}")
    print(f"TOTAL volume = {tot_v:.1f} m3 (target 2726)   weight = {tot_w:.1f} t (target 1828)")
    print(f"  LED  class: {led_v:.1f} m3")
    print(f"  SOFT class: {soft_v:.1f} m3")


if __name__ == "__main__":
    main()
