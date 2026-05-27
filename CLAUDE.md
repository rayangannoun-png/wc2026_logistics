# CLAUDE.md — Read this first

> This file is auto-loaded by Claude Code at the start of every session.
> It tells you what this repository is, how it is organised, and where to find
> the full context. **Read `docs/00_CONTEXT_FOR_CLAUDE.md` next** — it contains
> the complete decision history behind every modelling choice.

## What this project is

A **Sustainable Logistics Operations (SLO / MGT-530)** course project at
HEC Lausanne / EPFL (E4S, MSc Sustainable Management & Technology, Spring 2026,
Prof. Olivier Gallay).

**Topic:** optimising the distribution of FIFA World Cup 2026 venue branding /
signage from China to the 16 host stadiums across the USA, Canada and Mexico.

The project has **two parts**, two different optimisation problems:

| | Part I | Part II |
|---|---|---|
| Material | Generic branding (99.8% of volume) | Nominative material (flags, "A vs B" decals) |
| Volume | ~2,726 m³ | ~6.5 m³ |
| Known | Months ahead | 1–6 days before each match |
| Model | Deterministic LRP (cost min) | Two-stage stochastic (cost min, time hard constraint) |
| Course chapters | Facility location + packing (Ch. 8–9) | Stochastic + time windows (Ch. 2, 6) |
| Solver | SCIP via OR-Tools `pywraplp` | SCIP via OR-Tools `pywraplp` |

## How to run

```bash
pip install -r requirements.txt

# Part I
python -m src.part1_lrp.build_demand      # build per-stadium demand (LED+soft)
python -m src.part1_lrp.run               # solve LRP + set-up comparison
python -m src.part1_lrp.sensitivity       # OAT sensitivity

# Part II
python -m src.part2_stochastic.scenarios  # Monte-Carlo group-stage -> 50 scenarios
python -m src.part2_stochastic.model      # two-stage stochastic MILP
python -m src.part2_stochastic.sensitivity

# Figures
python -m src.common.visualize            # all PNGs into outputs/figures/
```

All scripts run from the **repo root** and write to `outputs/`.

## Repository layout

```
data/raw/          original project CSVs (network, ports, depots, edges, ...)
data/generated/    data WE build (stadium demand, scenarios)
docs/              **full context for you, Claude Code** — read these
reference/         the source material the project is built on (inventory, etc.)
src/common/        data loader + visualisations
src/part1_lrp/     deterministic Location-Routing Problem
src/part2_stochastic/  two-stage stochastic program
outputs/results/   solver outputs (CSV/JSON)
outputs/figures/   PNG figures
```

## Reading order for full context

1. `docs/00_CONTEXT_FOR_CLAUDE.md` — the whole story, all decisions
2. `docs/01_problem_definition.md`
3. `docs/02_part1_model_spec.md`
4. `docs/03_part2_model_spec.md`
5. `docs/04_assumptions_registry.md` — every assumption + how it is justified
6. `docs/05_data_dictionary.md` — every CSV, every column
7. `docs/06_sensitivity_plan.md`
8. `docs/07_visualization_plan.md`
9. `docs/08_report_structure.md` — how to write the report (DMAI, exec summary)
10. `docs/09_sources.md` — full source registry (what each source justifies)

## Hard rules for this project (do not violate)

- **Everything in English** (code, docs, comments).
- **Every assumption must be sourced or justified** (web source, derivation
  from project data, or explicitly assumed scenario with sensitivity). See
  `docs/04_assumptions_registry.md`.
- The **old report** (a previous MGT-530 PDF) is intentionally NOT used as a
  modelling reference. This repo is a fresh, extended model. Do not reintroduce
  it as a baseline unless explicitly asked.
- Keep models solvable with course tools (OR-Tools) in reasonable time.

## Current status (what already works)

- Part I LRP: solves to optimality, ~\$458k, 71 FEU (42 LED + 29 soft).
- Part II stochastic: solves, ~\$302k expected, 6/16 matches forced anticipatory.
- Both sensitivities and all 5 figures generate cleanly.
