# 02 — Part I model specification (deterministic LRP)

Implemented in `src/part1_lrp/model.py`. Demand built by
`src/part1_lrp/build_demand.py`.

## Demand construction (3 ventilation keys)

The inventory gives totals per poste; stadiums differ in size, so each poste is
ventilated with the key that matches its physics:

| Key | Postes | Rule |
|---|---|---|
| **capacity** | interior, seat covers, building wraps, vehicle wraps | ∝ seating capacity |
| **fixed** | LED perimeter, pitch-side, wayfinding, alu totems, masts, fence scrim | equal per stadium (LED = 67 m³/stadium, pitch is 105×68 m everywhere, scrim is precinct perimeter) |
| **typology** | brand scrubbing | 3 tiers from inventory B.3 (8 heavily-branded @6000 m², 5 recent @3000, 3 MX/CA @2100) |

Two freight classes: **LED** = poste `led_perimeter` only; **SOFT** = all else.
Reconciliation (verified): 2,726.0 m³ / 1,828.0 t; LED 1,072 / soft 1,654 m³.

## Sets

- `S` stadiums (16), `P` ports (5), `D` depots (7)

## Parameters

- `Vsoft_s, Vled_s` demand volume per stadium per class (m³)
- `ρ_LED = 0.994`, `ρ_SOFT = 0.46` t/m³ (from inventory Partie G weights)
- `FEU = 67` m³, `PAYLOAD = 26` t, `TRUCK = 90` m³
- `fcl_p, lcl_p, customs_p, handling_p` port costs
- `fixed_d, handling_d` depot costs
- `cost_truck(a)` = distance·cost_per_km + border, per road arc `a`

## Decision variables

- `open_p, open_d ∈ {0,1}`
- `feu_led_p, feu_soft_p ∈ ℤ⁺` containers per class per port
- `lcl_soft_p ≥ 0` (only ports with an LCL rate)
- `xs_{p,d} ≥ 0` soft port→depot; `yd_{d,s} ≥ 0` soft depot→stadium
- `xl_{p,s} ≥ 0` LED direct port→stadium
- `ntk_pd, ntk_ds, ntk_ps ∈ ℤ⁺` whole trucks per arc

## Objective (minimise)

```
  Σ_p (feu_led_p+feu_soft_p)·(fcl_p+handling_p) + open_p·customs_p   [ocean]
+ Σ_p lcl_soft_p·lcl_p                                               [LCL]
+ Σ_d open_d·fixed_d                                                 [depot open]
+ Σ_d (Σ_s yd_{d,s})·handling_d                                      [depot handling]
+ Σ_a ntk_a·cost_truck(a)   over port→depot, depot→stadium, port→stadium
```

## Constraints

1. **Demand per class:** Σ_d yd_{d,s} = Vsoft_s ; Σ_p xl_{p,s} = Vled_s ∀s
2. **Flow conservation (soft) at depot:** Σ_p xs_{p,d} = Σ_s yd_{d,s} ∀d
3. **Multidim sea capacity per port, per class:**
   - soft volume: Σ_d xs_{p,d} ≤ feu_soft_p·67 + lcl_soft_p
   - soft weight: Σ_d xs_{p,d}·ρ_SOFT ≤ feu_soft_p·26 + lcl_soft_p·ρ_SOFT
   - led volume: Σ_s xl_{p,s} ≤ feu_led_p·67
   - **led weight: Σ_s xl_{p,s}·ρ_LED ≤ feu_led_p·26**  ← the binding one
4. **Open coupling (big-M):** flows > 0 ⟹ open_p / open_d = 1
5. **Whole-truck packing:** ntk_a·90 ≥ volume on arc a

## Solver

SCIP via `pywraplp`. Baseline solves in well under a second.

## Alternative set-ups (for comparison, guideline p.6)

`solve_lrp(led_direct, use_depots, enforce_weight, allow_lcl)` — see
`run.py::run_comparison`. The weight-on/off contrast is the key one.

## Baseline result

\$458,626 total; 71 FEU (42 LED + 29 soft); open ports LA + NY + Vancouver;
open depots LAX + EWR. Cost dominated by ocean (~\$310k) then depot→stadium
trucking (~\$59k).
