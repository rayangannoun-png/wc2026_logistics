# 05 — Data dictionary

Two locations: `data/raw/` (original project data, read-only spirit) and
`data/generated/` (built by our scripts).

---

## data/raw/nodes.csv  (35 rows)
Master list of every physical/proxy location.

| column | meaning |
|---|---|
| node_id | unique id used everywhere (e.g. STAD_LA, PORT_LA_LB, DFW_DEPOT_NODE) |
| node_name, city, region, country | descriptive |
| node_type | port_gateway / candidate_depot / stadium / production_site |
| latitude, longitude | coordinates (used for the map) |
| confidence, status, notes | provenance metadata |

## data/raw/ports.csv  (6 rows; 5 usable, Veracruz excluded)
| column | meaning |
|---|---|
| node_id | links to nodes.csv |
| fcl_rate_feu_usd | ocean freight per FEU (FCL) China→port. **Empty for Veracruz** → excluded. |
| lcl_rate_m3_usd | LCL rate per m³ (**empty for Manzanillo** → no LCL var created) |
| customs_fixed_cost_usd | per open port |
| handling_cost_per_feu_usd | per FEU handled |
| sea_distance_from_china_km | for emissions/context |

## data/raw/depots.csv  (7 rows)
| column | meaning |
|---|---|
| node_id | links to nodes.csv |
| fixed_setup_cost_usd | cost to open the depot |
| handling_cost_per_m3_usd | per m³ throughput |
| capacity_proxy_m3 | **empty** → we model UFLP (uncapacitated) |

## data/raw/stadiums.csv  (16 rows)
node_id, fifa/common names, host_city, metro_area, country, venue_cluster.

## data/raw/production_sites.csv  (6 rows)
The Look Company + Wasserman Live sites + China origin proxy. `materials_possible`
lists what each can print. Used in Part II.

## data/raw/storage_scenarios.csv  (3 rows)
scenario_id (low/base/high), storage_cost_per_m3_day_usd (0.03/0.08/0.15).
`basis` states these are assumptions (FIFA costs not public).

## data/raw/edges.csv  (524 rows)
Candidate transport links.
| column | meaning |
|---|---|
| origin_node_id, destination_node_id | endpoints |
| edge_type | production_site_to_port_gateway, port_gateway_to_depot, depot_to_stadium, port_gateway_to_stadium, production_site_to_stadium, ... |
| mode | sea (5 edges, China→ports) or road (519) |
| distance_km, transit_time_days | road distances via OpenRouteService HGV profile (fallback haversine×1.25) |
| cost_per_km_usd | trucking rate (varies by region) |
| border_crossing, border_cost_usd | US/MX or US/CA crossing premium |

Derived in code: `cost_per_truck = distance_km·cost_per_km + border_cost`.

---

## data/generated/stadium_demand_by_poste.csv
Built by `build_demand.py`. One row per (stadium, poste): node_id, stadium_id,
poste, class (led/soft), volume_m3, weight_t.

## data/generated/stadium_demand_by_class.csv
Aggregated per stadium: vol_led_m3, wt_led_t, vol_soft_m3, wt_soft_t,
vol_total_m3, wt_total_t. **This is what the Part I model reads.** Totals
reconcile to 2,726.0 m³ / 1,828.0 t.

## data/generated/part2_scenarios.csv
Built by `scenarios.py`. One row per (scenario, match): scenario, probability,
match, home_team, away_team, venue_node, date. 50 scenarios × 16 matches.

---

## outputs/results/
- part1_summary.json — baseline cost breakdown, open ports/depots, FEU counts
- part1_flows_soft.csv — soft depot→stadium flows
- part1_flows_led.csv — LED port→stadium flows
- part1_setup_comparison.csv — the 4 alternative set-ups
- part1_sensitivity.csv — OAT sweeps
- part2_sensitivity.csv — OAT sweeps + stage split

## outputs/figures/
5 PNGs (see `docs/07_visualization_plan.md`).
