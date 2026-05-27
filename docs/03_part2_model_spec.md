# 03 — Part II model specification (two-stage stochastic)

Implemented in `src/part2_stochastic/model.py`. Scenarios by
`src/part2_stochastic/scenarios.py`.

## Scenario generation (uncertainty pipeline)

1. **Team strength** = normalised implied probability from tournament-winner
   odds (user screenshots, margin removed). A STRENGTH PROXY, not a
   qualification probability. Validated vs Opta (Spain ~16.5%, France ~15%).
2. **Group stage Monte-Carlo:** each of the 12 groups ranked by a
   strength-weighted draw without replacement (Plackett-Luce style) → 1st/2nd/
   3rd. 50 runs.
3. **Best-thirds:** rank the 12 third-placed teams by strength, keep 8, assign
   them to the fixed bracket's 3rd-slots respecting each slot's allowed group
   pool.
4. **Bracket mapping:** positions → 16 fixed R32 matches (venue + date known).
5. Output: 50 equiprobable scenarios × 16 matches (home/away teams, venue, date).

## Two supply modes (this is "Voie 3")

- **Reactive** (stage-2): produce locally after the matchup is known, ship
  site→venue. Feasible iff `transit ≤ window − production_days`.
- **Anticipatory** (stage-1): pre-print finished material before results and
  pre-position at the venue. Always feasible, but covers several candidate
  teams → **waste factor** (default 2×).

## Parameters

- `vol_per_match = 275 m² · (0.00056/0.57) ≈ 0.270 m³`
- `prod_cost = $50/m²` → converted to $/m³; `production_days = 1` (rush)
- `anticipatory_waste = 2.0`; `storage_cost` from scenario; `WAIT_DAYS = 30`
- `window(m) = match_date(m) − 27 June`

## Decision variables

- `a_m ≥ 0` anticipatory finished volume pre-positioned for match m (stage 1)
- `z_{sc,m,j} ≥ 0` reactive volume produced at site j for match m in scenario
  sc (only created when reactive-feasible)

## Objective (minimise)

```
  Σ_m a_m·(waste·prodcost_m3 + storage·WAIT_DAYS)              [stage 1]
+ Σ_sc prob_sc · Σ_m Σ_j (prodcost_m3 + truck_m3(j→venue))·z  [E[stage 2]]
```

## Constraints

1. **Each match served per scenario:** Σ_j z_{sc,m,j} + a_m ≥ vol_per_match
   ∀ sc, m  (reactive + anticipatory cover the demand)
2. Reactive variables exist only for time-feasible (site, match) pairs.

## Key result

6 of 16 matches are **forced anticipatory** (no reactive site in time):
matches 73 (LA, +1d), 74, 75, 76, 78, 79 (Boston/Monterrey/Houston/Dallas/
Mexico, early + far from sites). Total ~\$302k expected (\$165k stage-1 +
\$137k stage-2). Same-day production (0 days) reduces forced-anticipatory from
6 to 3 — production speed is a real lever.

## Why a single MILP

50 scenarios is small enough to solve the **deterministic equivalent**
directly (one MILP containing all scenarios), which is exact and simplest to
explain (course Chapter 2). No Benders decomposition needed.

## Notes / possible extensions for Claude Code

- The site-usage frequency printed by the model sums over scenario×match, so it
  can exceed 100%; it is a cumulative frequency, not a share. Could be
  normalised if a cleaner metric is wanted.
- Strength could be replaced by qualification-specific odds if available.
- Value of the Stochastic Solution (VSS) / EVPI could be computed explicitly by
  also solving the wait-and-see and expected-value problems.
