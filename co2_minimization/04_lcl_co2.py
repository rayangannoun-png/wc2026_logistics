"""
LCL CO₂ minimization — soft cargo only (vinyl, scrim, seat covers).

LED perimeter boards excluded: assumed rented locally within North America.
CO₂ calculated from actual cargo weight (LCL advantage: no FEU rounding).
  Ocean CO₂ (soft) = 16 g/tonne-km × (vol_soft_at_port × RHO_SOFT) × sea_dist_km / 1e3 kg
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lrp_model_v2 import (
    read_arc_cost_matrix, read_csv_dict, read_demand_v2,
    RHO_SOFT, TRUCK_CAPACITY_M3,
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

SEA_DIST = {
    "D01": 10_200,
    "D02": 21_100,
    "D03": 22_200,
    "D04":  8_500,
    "D05": 10_900,
    "D06": 19_500,   # Veracruz (via Panama Canal)
}

OCEAN_CO2_G_PER_TONNE_KM = 16.0
TRUCK_CO2_KG_PER_KM      = 1.0

# kg CO₂ per m³ of soft cargo per km of sea route
OCEAN_CO2_KG_PER_M3_KM = {
    d: OCEAN_CO2_G_PER_TONNE_KM * RHO_SOFT * SEA_DIST[d] / 1e3
    for d in SEA_DIST
}

LCL_RATE  = {"D01": 85.0, "D02": 100.0, "D03": 110.0, "D04": 82.0, "D05": 130.0, "D06": 135.0}
LCL_FIXED = {"D01": 4700.0, "D02": 4700.0, "D03": 4700.0, "D04": 2600.0, "D05": 5500.0, "D06": 5500.0}


def read_road_distance(filename):
    dist = {}
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)[1:]
        for row in reader:
            fn = row[0]
            for i, val in enumerate(row[1:]):
                dist[(fn, header[i])] = float(val)
    return dist


def solve_lcl_co2(node_ids, road_dist, port_variable,
                  demands_soft, verbose=True):
    stadiums = [n for n in node_ids if n.startswith("S")]
    depots   = [d for d in node_ids if d.startswith("D") and d in SEA_DIST]

    model = pulp.LpProblem("WC2026_CO2_LCL_softonly", pulp.LpMinimize)

    y     = pulp.LpVariable.dicts("y", depots, cat="Binary")
    z     = {(s, d): pulp.LpVariable(f"z_{s}_{d}", cat="Binary")
             for s in stadiums for d in depots}
    ntk   = {(s, d): pulp.LpVariable(f"ntk_{s}_{d}", lowBound=0, cat="Integer")
             for s in stadiums for d in depots}

    vol_soft = {d: pulp.lpSum(demands_soft[s] * z[(s, d)] for s in stadiums)
                for d in depots}

    # Ocean CO₂: proportional to actual weight (LCL advantage — no FEU rounding)
    ocean_co2 = pulp.lpSum(OCEAN_CO2_KG_PER_M3_KM[d] * vol_soft[d] for d in depots)

    # Truck CO₂: soft truck trips only
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

    solver = pulp.PULP_CBC_CMD(msg=verbose, timeLimit=600, gapRel=0.01)
    model.solve(solver)

    obj = pulp.value(model.objective)
    var = model.variablesDict()
    used = [d for d in depots if round(pulp.value(var.get("y_" + d)) or 0) == 1]

    soft_vol = {d: sum(demands_soft[s] * round(pulp.value(var.get(f"z_{s}_{d}")) or 0)
                       for s in stadiums) for d in depots}

    cost_soft_lcl = sum(LCL_RATE.get(d, 0) * soft_vol[d] for d in used)
    cost_fixed    = sum(LCL_FIXED.get(d, 0) for d in used)

    return {
        "status":              pulp.LpStatus[model.status],
        "used_ports":          sorted(used),
        "soft_vol_m3":         {d: round(soft_vol[d], 1) for d in used},
        "total_co2_t":         round(obj / 1000, 2),
        "indicative_cost_usd": round(cost_fixed + cost_soft_lcl, 0),
    }


def main():
    node_ids, _ = read_arc_cost_matrix(ARC_COST_FILE)
    road_dist    = read_road_distance(str(DIST_FILE))
    port_variable = read_csv_dict(PORT_VAR_FILE, "node_id", "variable_per_feu")
    demands_soft, demands_led = read_demand_v2(DEMAND_FILE)

    print("Solving LCL CO₂-optimal (soft cargo only)...")
    res = solve_lcl_co2(node_ids, road_dist, port_variable, demands_soft)

    print(f"\n=== LCL CO₂ RESULTS (soft only) ===")
    print(f"Status: {res['status']}")
    print(f"Ports ({len(res['used_ports'])}): {' + '.join(res['used_ports'])}")
    for d in res["used_ports"]:
        print(f"  {d}: {res['soft_vol_m3'][d]:.0f} m³ soft (LCL)")
    print(f"Total CO₂:       {res['total_co2_t']:.1f} t")
    print(f"Indicative cost: ${res['indicative_cost_usd']:,.0f}")


if __name__ == "__main__":
    main()
