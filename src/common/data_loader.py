"""
Common data-loading utilities for the FIFA WC2026 logistics model.

All CSVs live in data/raw/ (original project data) and data/generated/
(data produced by our own scripts, e.g. the per-stadium demand vector).

This module centralises path handling and CSV parsing so that both Part I
(deterministic LRP) and Part II (two-stage stochastic) read the same data
the same way.
"""
from __future__ import annotations

import csv
import os
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# This file is at: <repo>/src/common/data_loader.py
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
RAW_DIR = os.path.join(REPO_ROOT, "data", "raw")
GENERATED_DIR = os.path.join(REPO_ROOT, "data", "generated")
OUTPUTS_DIR = os.path.join(REPO_ROOT, "outputs")
RESULTS_DIR = os.path.join(OUTPUTS_DIR, "results")
FIGURES_DIR = os.path.join(OUTPUTS_DIR, "figures")


def _read_csv(path: str) -> List[Dict[str, str]]:
    """Read a CSV file into a list of dict rows (utf-8, handles \\r\\n)."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


# ---------------------------------------------------------------------------
# Physical / logistics constants (see docs/04_assumptions_registry.md)
# ---------------------------------------------------------------------------
FEU_VOLUME_M3 = 67.0      # interior volume of a 40ft container (ISO standard)
FEU_PAYLOAD_T = 26.0      # realistic payload limit (US road limit, < ISO 26.7t)
TRUCK_VOLUME_M3 = 90.0    # usable volume of a US dry-van trailer
FILL_RATE = 0.57          # realistic container fill rate (rolls + voids)

# Freight-class densities (t/m3), derived from Partie G of the WC2026 inventory
RHO_LED = 0.994           # LED perimeter boards: weight-driven
RHO_SOFT = 0.46           # soft material (vinyl/fabric/mesh): volume-driven


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------
def load_ports(include_excluded: bool = False) -> Dict[str, dict]:
    """
    Ocean gateways. Veracruz (PORT_VER) is excluded by default because it has
    no FCL rate (no direct FCL offering found in the source report).

    Returns dict keyed by node_id with: fcl, lcl (or None), customs, handling,
    sea_distance_km, coast, country.
    """
    rows = _read_csv(os.path.join(RAW_DIR, "ports.csv"))
    out: Dict[str, dict] = {}
    for r in rows:
        has_fcl = r["fcl_rate_feu_usd"].strip() != ""
        if not has_fcl and not include_excluded:
            continue
        out[r["node_id"]] = dict(
            port_id=r["port_id"],
            name=r["port_name"],
            country=r["country"],
            coast=r["coast"],
            fcl=float(r["fcl_rate_feu_usd"]) if has_fcl else None,
            lcl=float(r["lcl_rate_m3_usd"]) if r["lcl_rate_m3_usd"].strip() else None,
            customs=float(r["customs_fixed_cost_usd"]),
            handling=float(r["handling_cost_per_feu_usd"]),
            sea_distance_km=float(r["sea_distance_from_china_km"])
            if r["sea_distance_from_china_km"].strip() else None,
        )
    return out


def load_depots() -> Dict[str, dict]:
    """Candidate depots. capacity_proxy_m3 is empty in source -> UFLP (uncapacitated)."""
    rows = _read_csv(os.path.join(RAW_DIR, "depots.csv"))
    out: Dict[str, dict] = {}
    for r in rows:
        out[r["node_id"]] = dict(
            depot_id=r["depot_id"],
            role=r["depot_role"],
            region=r["region_served"],
            fixed=float(r["fixed_setup_cost_usd"]),
            handling_m3=float(r["handling_cost_per_m3_usd"]),
        )
    return out


def load_stadiums() -> Dict[str, dict]:
    """16 host venues, keyed by node_id."""
    rows = _read_csv(os.path.join(RAW_DIR, "stadiums.csv"))
    out: Dict[str, dict] = {}
    for r in rows:
        out[r["node_id"]] = dict(
            stadium_id=r["stadium_id"],
            fifa_name=r["fifa_venue_name"],
            common_name=r["common_stadium_name"],
            city=r["host_city"],
            metro=r["metro_area"],
            country=r["country"],
            cluster=r["venue_cluster"],
        )
    return out


def load_production_sites() -> Dict[str, dict]:
    """Production sites for Part II (printing). Includes China origin proxy."""
    rows = _read_csv(os.path.join(RAW_DIR, "production_sites.csv"))
    out: Dict[str, dict] = {}
    for r in rows:
        out[r["node_id"]] = dict(
            production_id=r["production_id"],
            company=r["company"],
            role=r["site_role"],
            confirmed=r["confirmed"],
            materials=r["materials_possible"],
        )
    return out


def load_storage_scenarios() -> Dict[str, dict]:
    """Low/base/high storage cost per m3 per day (USD)."""
    rows = _read_csv(os.path.join(RAW_DIR, "storage_scenarios.csv"))
    return {
        r["scenario_id"]: dict(
            cost_per_m3_day=float(r["storage_cost_per_m3_day_usd"]),
            description=r["scenario_description"],
        )
        for r in rows
    }


def load_road_edges() -> Dict[Tuple[str, str], dict]:
    """
    Road edges keyed by (origin_node_id, destination_node_id).

    cost_per_truck = distance_km * cost_per_km_usd + border_cost_usd
    (a truck pays the full traversal cost; we count whole trucks elsewhere).
    """
    rows = _read_csv(os.path.join(RAW_DIR, "edges.csv"))
    out: Dict[Tuple[str, str], dict] = {}
    for r in rows:
        if r["mode"] != "road":
            continue
        o, d = r["origin_node_id"], r["destination_node_id"]
        dist = float(r["distance_km"])
        cpk = float(r["cost_per_km_usd"])
        border = float(r["border_cost_usd"]) if r["border_cost_usd"].strip() else 0.0
        out[(o, d)] = dict(
            edge_type=r["edge_type"],
            distance_km=dist,
            transit_time_days=float(r["transit_time_days"])
            if r["transit_time_days"].strip() else None,
            cost_per_km=cpk,
            border_cost=border,
            cost_per_truck=dist * cpk + border,
        )
    return out


def load_sea_edges() -> Dict[Tuple[str, str], dict]:
    """Sea edges (China -> port), keyed by (origin, destination)."""
    rows = _read_csv(os.path.join(RAW_DIR, "edges.csv"))
    out: Dict[Tuple[str, str], dict] = {}
    for r in rows:
        if r["mode"] != "sea":
            continue
        o, d = r["origin_node_id"], r["destination_node_id"]
        out[(o, d)] = dict(
            distance_km=float(r["distance_km"]) if r["distance_km"].strip() else None,
        )
    return out


def load_stadium_demand() -> Dict[str, dict]:
    """
    Per-stadium demand, split into LED and soft classes.

    Built by src/part1_lrp/build_demand.py from the WC2026 inventory.
    Returns dict keyed by stadium node_id with:
      vol_led, wt_led, vol_soft, wt_soft, vol_total, wt_total
    """
    path = os.path.join(GENERATED_DIR, "stadium_demand_by_class.csv")
    rows = _read_csv(path)
    out: Dict[str, dict] = {}
    for r in rows:
        out[r["node_id"]] = dict(
            vol_led=float(r["vol_led_m3"]),
            wt_led=float(r["wt_led_t"]),
            vol_soft=float(r["vol_soft_m3"]),
            wt_soft=float(r["wt_soft_t"]),
            vol_total=float(r["vol_total_m3"]),
            wt_total=float(r["wt_total_t"]),
        )
    return out


if __name__ == "__main__":
    # Quick smoke test
    print("Ports (with FCL):", list(load_ports().keys()))
    print("Depots:", list(load_depots().keys()))
    print("Stadiums:", len(load_stadiums()))
    print("Production sites:", list(load_production_sites().keys()))
    print("Storage scenarios:", load_storage_scenarios())
    print("Road edges:", len(load_road_edges()))
    print("Sea edges:", len(load_sea_edges()))
