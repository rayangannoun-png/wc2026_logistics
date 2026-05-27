# 01 — Problem definition

## The decision-maker

FIFA's venue-dressing logistics operation for the 2026 World Cup. All branding
material is assumed to originate in China and must reach the 16 host stadiums.
The operation acts as a **decision-aid tool**: which ports/depots/production
sites to use, how to pack and route, at minimum cost (Part I) and how to
guarantee on-time delivery under uncertainty (Part II).

## Geography (the network)

- **Origin:** China (Shanghai proxy).
- **Ports (ocean gateways):** Los Angeles/Long Beach, New York/New Jersey,
  Houston, Vancouver, Manzanillo (Veracruz excluded — no FCL offering).
- **Depots (candidates):** 7 proxy depots (Dallas, Mexico City, Toronto,
  Vancouver, LA/Inland Empire, Newark, Miami).
- **Production sites (Part II):** The Look Company (Barrie, Tukwila, Tampa),
  Wasserman Live (Tempe, North Carolina).
- **Stadiums:** the 16 host venues.

## The two problems

### Part I — deterministic Location-Routing (Cat 1)
Flow: China → port (sea, FCL/LCL) → depot (truck) → stadium (truck), with LED
going direct port → stadium. Objective: **minimise total cost**. All demand
known in advance. ~2,726 m³.

### Part II — two-stage stochastic, time-critical (Cat 2)
Flow: raw material China → site (sea, in advance) → wait → (results) →
local print → stadium, within a tight window. Objective: **minimise expected
cost**, with **time as a hard constraint**. ~6.5 m³ but uncertain and urgent.

## Why this is a good SLO project

- Real organisation, real venues, real network, real cost structure.
- Uses three course pillars: **facility location** (ports/depots/sites),
  **packing** (multidimensional FEU volume+weight), and **stochastic /
  time-window** reasoning (Part II).
- Produces concrete managerial recommendations (where to open hubs, why LED
  dominates the container count, which matches must be pre-positioned).

## Scope choices

- Perimeter = stadiums + immediate precinct; **city dressing excluded** (as in
  the Qatar 2022 baseline), consistent with the inventory.
- "All from China" including LED (defensible upper bound for sizing).
- Part II restricted to the **Round of 32** (first knockout round = maximum
  uncertainty, the moment the bracket first fills).
