# 06 — Sensitivity analysis plan

The course brief explicitly asks for sensitivity analysis. Method: **One-At-A-
Time (OAT)** — vary one parameter across a defensible range, re-solve, record
total cost and whether the optimal structure changes.

## Part I (`src/part1_lrp/sensitivity.py`)

| Parameter | Values | What it reveals |
|---|---|---|
| weight constraint | on / off | **Headline:** 71 FEU / \$458k vs 40 FEU / \$324k — the LED weight effect. |
| LCL policy | lcl allowed / FCL-only | LCL only helps at the margin (\$458k vs \$461k). |
| LED routing | direct / via depot | Direct slightly dearer in trucking (\$458k vs \$443k). |

(Storage is excluded from Part I by design, so it is not swept here; storage
sensitivity lives in Part II.)

Additional sweeps Claude Code can add if wanted: demand ±10% (stadium-size
factor), per-port ocean rate ±, trucking rate ±, depot fixed cost ±.

## Part II (`src/part2_stochastic/sensitivity.py`)

| Parameter | Values | What it reveals |
|---|---|---|
| storage scenario | low / base / high | Negligible on total (storage tiny vs production) — confirms robustness. |
| production cost | \$20 / \$50 / \$86 per m² | Dominant driver: \$121k → \$302k → \$520k. |
| anticipatory waste | 1× / 2× / 3× | Cost of uncertainty: more candidate teams → dearer stage-1. |
| production days | 0 (same-day) / 1 (rush) | Forced-anticipatory matches 3 vs 6 — production speed is a real lever. |

## How to read it in the report

- Show a tornado-style or grouped-bar chart per part.
- Flag any parameter that **changes the optimal network/structure** (e.g.
  weight on/off flips the FEU count and cost regime).
- Tie each finding to a managerial recommendation (see `docs/08`).
