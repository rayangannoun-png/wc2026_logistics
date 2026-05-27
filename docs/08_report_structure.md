# 08 — Report structure (how to write the deliverable)

The brief asks for a **synthetic written report with an executive summary**,
plus slides. Follow the **Define – Measure – Analyze – Improve (DMAI)** thread
suggested in the brief (p.6).

## Executive summary (½–1 page, write last)

- The problem in 2 sentences (distribute WC2026 branding China→16 stadiums;
  two parts: cost-optimal generic flow + time-critical stochastic nominative).
- Headline numbers: Part I ~\$458k / 71 FEU (LED weight effect raises it from
  40 FEU); Part II ~\$302k expected, 6/16 R32 matches forced anticipatory.
- Top 3 managerial recommendations (below).

## DMAI structure

### Define
- Practical situation, the organisation, the two material categories,
  the network. (Use `docs/01`.)

### Measure
- Data sources and parameters; how demand was built (3 keys); how scenarios
  were generated; the assumptions registry (`docs/04`, `docs/05`, `docs/09`).
- State openly which numbers are sourced / derived / assumed-with-sensitivity.

### Analyze
- Mathematical formulations (`docs/02`, `docs/03`).
- Baseline results + figures (`docs/07`).
- Sensitivity analysis (`docs/06`).
- Set-up comparison (weight on/off; LED direct/via depot; FCL-only; same-day).

### Improve (managerial insights & recommendations)
1. **LED dominates the container count via weight, not volume.** Counting only
   volume understates FEU by ~44% (40 vs 71). Recommendation: treat LED as a
   separate, weight-driven, FCL/flat-rack stream; consider local LED rental to
   cut ~half the containers.
2. **Two hubs (West + East) are cost-optimal**; depots sit on the ports, so the
   real cost levers are ocean rates and last-mile trucking, not depot location.
3. **6 of 16 R32 matches cannot be served reactively** (window too short, esp.
   LA day +1 and Mexican venues) → they REQUIRE anticipatory pre-positioning of
   finished nominative material. Faster (same-day) production would cut this to
   3. Recommendation: pre-kit candidate-team flags for short-window venues.

## Code in appendix
Reference the repo; the `src/` modules are the appendix. Mention that all
results are reproducible via the commands in `CLAUDE.md` / `README.md`.

## Slides (15 min + 10 Q&A)
~10–12 slides: problem, network map, Part I formulation + headline FEU figure,
sensitivity, Part II concept (two stages), feasibility figure, stage split,
recommendations. Lead with the LED-weight and the 6-forced-matches insights —
they are the most memorable.

## Administrative
- Report deadline was originally 26 May, slides 27 May 20:00, presentation
  28 May (extended for this team).
- **Peer review** (individual) due 1 June 18:00: each member allocates 100%
  across the group reflecting contribution. Do not forget it.
