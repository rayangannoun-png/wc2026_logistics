"""
LRP model v2 — two freight classes with weight constraint.

Freight classes
---------------
SOFT  : vinyl, fabric, totems, brand-scrubbing (~0.46 t/m³)
        → volume-driven FEU count; multiple truck trips per stadium
LED   : LED perimeter boards (~0.994 t/m³, fragile)
        → weight-driven FEU count (26 t payload fills before 67 m³ volume)
        → 1 dedicated truck per stadium (67 m³ < 90 m³ truck cap)

Truck model
-----------
With updated demands (77–126 m³/stadium for SOFT, 67 m³ for LED), many
stadiums need more than one truckload. The MTZ single-route VRP is therefore
replaced by integer truck-trip counts per arc — the same approach used in
the team's Part-I reference model (src/part1_lrp/model.py).

  ntk_soft[d,s] = integer truck trips from port d to stadium s for SOFT
  LED always fits in 1 truck (67 < 90 m³), so LED trips = z[s,d]

Container parameters (sourced from inventory reconstruction, Partie G)
----------------------------------------------------------------------
  FEU interior volume : 67 m³  (ISO 40ft standard)
  FEU payload         : 26 t   (US road enforcement)
  ρ_LED  = 0.994 t/m³           → weight-constrained
  ρ_SOFT = 0.460 t/m³           → just above weight threshold (26/67 ≈ 0.388)
  Truck cap : 90 m³  (US dry-van trailer, 16.15×2.5×2.7 m)
"""

import csv
import math
import pulp

CONTAINER_VOLUME_M3 = 67.0
CONTAINER_PAYLOAD_T = 26.0
RHO_LED              = 0.994
RHO_SOFT             = 0.460
TRUCK_CAPACITY_M3    = 90.0


def read_arc_cost_matrix(filename):
    with open(filename, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)[1:]
        cost = {}
        for row in reader:
            from_node = row[0]
            for i, val in enumerate(row[1:]):
                cost[(from_node, header[i])] = float(val)
    return header, cost


def read_csv_dict(filename, key_col, value_col):
    data = {}
    with open(filename, "r", newline="") as f:
        for row in csv.DictReader(f):
            data[row[key_col]] = float(row[value_col])
    return data


def read_demand_v2(filename):
    """Return (demands_soft, demands_led) dicts keyed by node_id."""
    soft, led = {}, {}
    with open(filename, "r", newline="") as f:
        for row in csv.DictReader(f):
            nid = row["node_id"]
            soft[nid] = float(row["vol_soft_m3"])
            led[nid]  = float(row["vol_led_m3"])
    return soft, led


def build_and_solve(node_ids, arc_cost, port_fixed, port_variable,
                    demands_soft, demands_led,
                    k=None, time_limit=1800, mip_gap=0.01, verbose=True):
    """
    Build and solve the two-class LRP.

    k : if given, forces exactly k ports open.
    Returns the solved PuLP model.
    """
    stadiums = [n for n in node_ids if n.startswith("S")]
    depots   = [n for n in node_ids if n.startswith("D")]

    label = "WC2026_LRP_v2" if k is None else f"WC2026_LRP_v2_K{k}"
    model = pulp.LpProblem(label, pulp.LpMinimize)

    # ── Variables ──────────────────────────────────────────────────────────────

    # Port open binary
    y = pulp.LpVariable.dicts("y", depots, cat="Binary")

    # Stadium-to-port assignment (shared by both classes)
    z = {(s, d): pulp.LpVariable(f"z_{s}_{d}", cat="Binary")
         for s in stadiums for d in depots}

    # Integer truck trips: SOFT deliveries from port d to stadium s (round-trip)
    ntk = {(s, d): pulp.LpVariable(f"ntk_{s}_{d}", lowBound=0, cat="Integer")
           for s in stadiums for d in depots}

    # Integer FEU counts per port per class
    n_soft = pulp.LpVariable.dicts("nsoft", depots, lowBound=0, cat="Integer")
    n_led  = pulp.LpVariable.dicts("nled",  depots, lowBound=0, cat="Integer")

    # ── Objective ──────────────────────────────────────────────────────────────
    # port fixed opening + ocean freight (both classes) + SOFT trucks + LED trucks
    model += (
        pulp.lpSum(port_fixed[d] * y[d] for d in depots)
        + pulp.lpSum(port_variable[d] * (n_soft[d] + n_led[d]) for d in depots)
        # SOFT truck cost: ntk round trips, port→stadium→port
        + pulp.lpSum(
            ntk[(s, d)] * (arc_cost[(d, s)] + arc_cost[(s, d)])
            for s in stadiums for d in depots
        )
        # LED truck cost: 1 direct round trip per stadium from assigned port
        + pulp.lpSum(
            z[(s, d)] * (arc_cost[(d, s)] + arc_cost[(s, d)])
            for s in stadiums for d in depots
        )
    )

    # ── Constraints ────────────────────────────────────────────────────────────

    if k is not None:
        model += pulp.lpSum(y[d] for d in depots) == k

    # Each stadium assigned to exactly one port
    for s in stadiums:
        model += pulp.lpSum(z[(s, d)] for d in depots) == 1

    for d in depots:
        # Assignment only to open port
        for s in stadiums:
            model += z[(s, d)] <= y[d]

        # Open port must serve at least one stadium
        model += pulp.lpSum(z[(s, d)] for s in stadiums) >= y[d]

        # SOFT truck trips must cover demand
        for s in stadiums:
            model += ntk[(s, d)] * TRUCK_CAPACITY_M3 >= demands_soft[s] * z[(s, d)]
            # ntk is zero when stadium not assigned to this port
            model += ntk[(s, d)] <= math.ceil(
                max(demands_soft.values()) / TRUCK_CAPACITY_M3
            ) * z[(s, d)]

        # SOFT FEU constraints: volume AND weight (weight is marginally binding)
        model += n_soft[d] * CONTAINER_VOLUME_M3 >= pulp.lpSum(
            demands_soft[s] * z[(s, d)] for s in stadiums
        )
        model += n_soft[d] * CONTAINER_PAYLOAD_T >= pulp.lpSum(
            demands_soft[s] * RHO_SOFT * z[(s, d)] for s in stadiums
        )

        # LED FEU constraints: volume AND weight (weight is strongly binding)
        model += n_led[d] * CONTAINER_VOLUME_M3 >= pulp.lpSum(
            demands_led[s] * z[(s, d)] for s in stadiums
        )
        model += n_led[d] * CONTAINER_PAYLOAD_T >= pulp.lpSum(
            demands_led[s] * RHO_LED * z[(s, d)] for s in stadiums
        )

    solver = pulp.PULP_CBC_CMD(msg=verbose, timeLimit=time_limit, gapRel=mip_gap)
    model.solve(solver)
    return model


def extract_results(model, depots, port_fixed, port_variable, demands_soft, demands_led):
    """Extract cost breakdown from a solved model."""
    obj = pulp.value(model.objective)
    if obj is None:
        return None

    status = pulp.LpStatus[model.status]
    if status not in ("Optimal", "Not Solved"):
        # Check if we have a feasible value despite non-optimal status
        if obj is None:
            return None

    var = model.variablesDict()

    used_ports = [d for d in depots if round(pulp.value(var.get("y_" + d)) or 0) == 1]
    total_fixed = sum(port_fixed[d] for d in used_ports)

    feu_soft = {d: round(pulp.value(var.get("nsoft_" + d)) or 0) for d in depots}
    feu_led  = {d: round(pulp.value(var.get("nled_"  + d)) or 0) for d in depots}
    total_variable = sum(
        port_variable[d] * (feu_soft[d] + feu_led[d]) for d in depots
    )
    total_trucking = obj - total_fixed - total_variable

    return {
        "status":            status,
        "used_ports":        sorted(used_ports),
        "feu_soft":          {d: feu_soft[d] for d in used_ports},
        "feu_led":           {d: feu_led[d]  for d in used_ports},
        "feu_total":         sum(feu_soft[d] + feu_led[d] for d in used_ports),
        "fixed_cost_usd":    round(total_fixed, 2),
        "variable_cost_usd": round(total_variable, 2),
        "trucking_cost_usd": round(total_trucking, 2),
        "total_cost_usd":    round(obj, 2),
    }
