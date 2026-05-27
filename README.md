# FIFA World Cup 2026 — Venue Branding Logistics Optimization

SLO / MGT-530 course project (HEC Lausanne / EPFL E4S, Spring 2026).
Optimising the distribution of FIFA World Cup 2026 venue branding from China to
the 16 host stadiums (USA / Canada / Mexico).

> **Claude Code users:** start with `CLAUDE.md`, then `docs/00_CONTEXT_FOR_CLAUDE.md`.

## Two parts

- **Part I — deterministic Location-Routing Problem (cost).** Generic branding
  (~2,726 m³). Ports → depots → stadiums, with a multidimensional
  (volume + weight) container constraint and a separate LED freight class.
- **Part II — two-stage stochastic program (time-critical).** Nominative
  material (flags, "A vs B" decals, ~6.5 m³) for the Round of 32 under team
  uncertainty; reactive local production vs anticipatory pre-positioning.

## Quick start

```bash
pip install -r requirements.txt
python run_all.py            # runs everything end-to-end
```

Or step by step:

```bash
python -m src.part1_lrp.build_demand
python -m src.part1_lrp.run
python -m src.part1_lrp.sensitivity
python -m src.part2_stochastic.scenarios
python -m src.part2_stochastic.model
python -m src.part2_stochastic.sensitivity
python -m src.common.visualize
```

## Headline results

- Part I: **~\$458k**, **71 FEU** (42 LED + 29 soft). Ignoring the weight
  ceiling would wrongly give 40 FEU — the **LED weight effect** is the key
  finding.
- Part II: **~\$302k** expected cost; **6 of 16** R32 matches must be served by
  **anticipatory pre-positioning** (window too short for reactive production).

## Layout

```
CLAUDE.md            entry point for Claude Code
docs/                full context, specs, assumptions, sources, report plan
data/raw/            original project CSVs
data/generated/      demand + scenarios we build
reference/           inventory reconstructions, course KB, tournament reference
src/common/          data loader + visualisations
src/part1_lrp/       deterministic LRP
src/part2_stochastic/  two-stage stochastic program
outputs/             results (CSV/JSON) + figures (PNG)
```

## Notes

- Everything is in English; every assumption is sourced, derived, or assumed
  with a sensitivity range (see `docs/04_assumptions_registry.md`).
- Solver: Google OR-Tools (SCIP via `pywraplp`).
