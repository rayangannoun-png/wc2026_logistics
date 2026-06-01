"""
FCL CO₂ minimization — soft cargo only (vinyl, scrim, seat covers).

LED perimeter boards excluded: assumed rented locally within North America,
not shipped from Asia. See report Section 3.1 for assumption justification.

Emission factors (GLEC Framework v3 / ISO 14083):
  Ship : 16 g CO₂ / tonne-km
  Truck: 1.0 kg CO₂ / km (EPA Phase-3 HDV baseline)

SOFT FEU weight: 0.46 t/m³ × 67 m³ = 30.8 t > 26 t payload → weight-limited.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lrp_model_v2 import (
    read_arc_cost_matrix, read_csv_dict, read_demand_v2,
    CONTAINER_VOLUME_M3, CONTAINER_PAYLOAD_T, RHO_SOFT, TRUCK_CAPACITY_M3,
)
import csv
import pulp

BASE_DIR    = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent.parent

ARC_COST_FILE   = PROJECT_DIR / "data" / "processed" / "arc_cost_matrix_usd.csv"
PORT_FIXED_FILE = PROJECT_DIR / "data" / "processed" / "port_fixed_costs_usd.csv"
PORT_VAR_FILE   = PROJECT_DIR / "data" / "processed" / "port_variable_costs_usd.csv"
DEMAND_FILE     = PROJECT_DIR / "data" / "processed" / "demand_v2.csv"
DIST_FILE       = PROJECT_DIR / "data" / "raw" / "distance_matrix_km(short_node_names).csv"

# Sea distances from Shanghai (km) — same source as Part I report
SEA_DIST = {
    "D01": 10_200,   # Los Angeles
    "D02": 21_100,   # New York
    "D03": 22_200,   # Houston
    "D04":  8_500,   # Vancouver
    "D05": 10_900,   # Manzanillo
    "D06": 19_500,   # Veracruz (via Panama Canal)
}

OCEAN_CO2_G_PER_TONNE_KM = 16.0   # GLEC v3 / ISO 14083
FEU_PAYLOAD_T            = 26.0   # tonnes per weight-limited FEU
TRUCK_CO2_KG_PER_KM      = 1.0    # EPA Phase-3 HDV

# kg CO₂ per FEU per sea route
OCEAN_CO2_KG_PER_FEU = {
    d: OCEAN_CO2_G_PER_TONNE_KM * FEU_PAYLOAD_T * SEA_DIST[d] / 1e3
    for d in SEA_DIST
}


def read_road_distance(filename):
    """Return distance matrix (km) for road arcs."""
    dist = {}
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)[1:]
        for row in reader:
            from_node = row[0]
            for i, val in enumerate(row[1:]):
                dist[(from_node, header[i])] = float(val)
    return dist


def solve_co2_fcl(node_ids, arc_cost, road_dist, port_fixed, port_variable,
                  demands_soft, verbose=True):
    stadiums = [n for n in node_ids if n.startswith("S")]
    depots   = [d for d in node_ids if d.startswith("D") and d in SEA_DIST]

    model = pulp.LpProblem("WC2026_CO2_FCL_softonly", pulp.LpMinimize)

    y     = pulp.LpVariable.dicts("y", depots, cat="Binary")
    z     = {(s, d): pulp.LpVariable(f"z_{s}_{d}", cat="Binary")
             for s in stadiums for d in depots}
    ntk   = {(s, d): pulp.LpVariable(f"ntk_{s}_{d}", lowBound=0, cat="Integer")
             for s in stadiums for d in depots}
    n_soft = pulp.LpVariable.dicts("nsoft", depots, lowBound=0, cat="Integer")

    # Ocean CO₂ (kg): soft FEUs × kg_CO2_per_FEU
    ocean_co2 = pulp.lpSum(OCEAN_CO2_KG_PER_FEU[d] * n_soft[d] for d in depots)

    # Truck CO₂ (kg): soft truck trips × round-trip distance
    truck_co2 = pulp.lpSum(
        ntk[(s, d)] * (road_dist[(d, s)] + road_dist[(s, d)]) * TRUCK_CO2_KG_PER_KM
        for s in stadiums for d in depots
    )

    model += ocean_co2 + truck_co2

    for s in stadiums:
        model += pulp.lpSum(z[(s, d)] for d in depots) == 1

    for d in depots:
        for s in stadiums:
            model += z[(s, d)] <= y[d]
        model += pulp.lpSum(z[(s, d)] for s in stadiums) >= y[d]

        for s in stadiums:
            model += ntk[(s, d)] * TRUCK_CAPACITY_M3 >= demands_soft[s] * z[(s, d)]
            model += ntk[(s, d)] <= math.ceil(
                max(demands_soft.values()) / TRUCK_CAPACITY_M3
            ) * z[(s, d)]

        model += n_soft[d] * CONTAINER_VOLUME_M3 >= pulp.lpSum(
            demands_soft[s] * z[(s, d)] for s in stadiums
        )
        model += n_soft[d] * CONTAINER_PAYLOAD_T >= pulp.lpSum(
            demands_soft[s] * RHO_SOFT * z[(s, d)] for s in stadiums
        )

    solver = pulp.PULP_CBC_CMD(msg=verbose, timeLimit=600, gapRel=0.01)
    model.solve(solver)

    obj = pulp.value(model.objective)
    var = model.variablesDict()
    used = [d for d in depots if round(pulp.value(var.get("y_" + d)) or 0) == 1]

    feu_soft = {d: round(pulp.value(var.get("nsoft_" + d)) or 0) for d in depots}
    ntk_vals = {(s, d): round(pulp.value(var.get(f"ntk_{s}_{d}")) or 0)
                for s in stadiums for d in depots}

    cost_fixed    = sum(port_fixed.get(d, 0) for d in used)
    cost_variable = sum(port_variable[d] * feu_soft[d] for d in used)
    cost_trucking = sum(
        ntk_vals[(s, d)] * (arc_cost.get((d, s), 0) + arc_cost.get((s, d), 0))
        for s in stadiums for d in depots
    )

    return {
        "status":            pulp.LpStatus[model.status],
        "used_ports":        sorted(used),
        "feu_soft":          {d: feu_soft[d] for d in used},
        "feu_total":         sum(feu_soft[d] for d in used),
        "total_co2_t":       round(obj / 1000, 2),
        "total_cost_usd":    round(cost_fixed + cost_variable + cost_trucking, 2),
    }


def main():
    node_ids, arc_cost = read_arc_cost_matrix(ARC_COST_FILE)
    road_dist    = read_road_distance(str(DIST_FILE))
    port_fixed   = read_csv_dict(PORT_FIXED_FILE, "node_id", "fixed_cost_usd")
    port_variable = read_csv_dict(PORT_VAR_FILE,  "node_id", "variable_per_feu")
    demands_soft, _ = read_demand_v2(DEMAND_FILE)

    print("Solving FCL CO₂-optimal (soft cargo only)...")
    res = solve_co2_fcl(node_ids, arc_cost, road_dist, port_fixed, port_variable, demands_soft)

    print(f"\n=== FCL CO₂ RESULTS (soft only) ===")
    print(f"Status: {res['status']}")
    print(f"Ports ({len(res['used_ports'])}): {' + '.join(res['used_ports'])}")
    for d in res["used_ports"]:
        print(f"  {d}: {res['feu_soft'][d]} soft FEUs")
    print(f"Total FEUs:  {res['feu_total']}")
    print(f"Total CO₂:   {res['total_co2_t']:.1f} t")
    print(f"Total cost:  ${res['total_cost_usd']:,.2f}")


if __name__ == "__main__":
    main()
