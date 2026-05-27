# 00 — Full context for Claude Code

> This is the most important document in the repo. It captures the **entire
> reasoning and decision history** behind the model, so that you (Claude Code)
> understand not just *what* the code does but *why* every choice was made.
> It was written by the human + an assistant over a long design conversation.

---

## 1. The real-world situation

FIFA World Cup 2026 is hosted across 16 stadiums in the USA (11), Mexico (3)
and Canada (2), 11 June – 19 July 2026, 48 teams, 104 matches. An enormous
amount of **venue branding / signage** must be manufactured and shipped (the
project assumes **all of it originates in China**) and distributed to the 16
stadiums. Two providers handle the real "Venue Dressing Programme": The Look
Company and Wasserman Live (ex-bluemedia).

We split the material into two categories with opposite logistics natures:

- **Cat 1 (Part I)** — generic tournament branding: fence scrim, building
  wraps, seat covers, LED perimeter boards, interior wraps, etc. ~2,726 m³,
  ~99.8% of volume. Known months ahead → plan for **cost**.
- **Cat 2 (Part II)** — nominative material: national flags, "Country A vs
  Country B" decals, team-specific press backdrops. ~6.5 m³, ~0.2% of volume.
  Cannot be made until the matchup is known (1–6 days before each knockout
  match) → plan for **time** under **uncertainty**.

This is the central paradox of the project: **0.2% of the volume carries 80%
of the modelling difficulty.**

---

## 2. Why the data demanded that we BUILD the demand ourselves

The project CSVs give the full logistics **network** (nodes, ports, depots,
edges with distances/costs/times, production sites) and all **cost
parameters** (FCL/LCL rates, customs, handling, depot costs, storage
scenarios). But there is **no per-stadium demand in m³**. The data README
references an `inventory_template.csv` that **is not present**.

So we built the per-stadium demand ourselves from the WC2026 inventory
reconstruction (`reference/Reconstitution_Inventaire_WC2026.md`), category by
category, using **three ventilation keys** (see `src/part1_lrp/build_demand.py`
and `docs/02_part1_model_spec.md`). The totals reconcile EXACTLY with the
inventory: **2,726.0 m³ / 1,828.0 t**, split into LED 1,072 m³ and soft
1,654 m³.

---

## 3. Part I — the model in plain words

ONE integrated MILP (a Location-Routing Problem) that decides simultaneously:
1. which **ports** to open (5 candidates; Veracruz excluded — no FCL rate),
   and FCL vs LCL per port;
2. which **depots** to open (7 candidates) and which port feeds which depot;
3. which **depot serves which stadium** (continuous flow).

**Two freight classes**, because the material does not behave uniformly:
- **LED** (~1000 kg/m³): FCL only, ships **direct port→stadium** (bypasses
  depots — 1 system/stadium, oversized/fragile; justified by the data README's
  "direct flows for oversized/pre-kitted shipments"). Its **weight** saturates
  the container (26 t) before its volume.
- **SOFT** (~460 kg/m³): FCL or LCL, flows **port→depot→stadium**. Its
  **volume** saturates the container (67 m³).

**The multidimensional container constraint** is the heart of Part I: each FEU
has TWO ceilings, 67 m³ AND 26 t, enforced per class per port. This is what
makes the LED FEU count jump from ~16 (if you only count volume) to ~42 (when
weight binds) — reproducing the 61→77 FEU "tipping" described in the inventory
(Partie G). We verified: weight ON → 71 FEU / \$458k; weight OFF → 40 FEU /
\$324k. **That gap is the project's headline result.**

Objective = ocean (FCL+LCL+customs+handling) + depot opening + depot handling
+ trucking (whole trucks on every arc). **Storage excluded** in Part I (Cat-1
transits, it does not sit in storage).

Decisions taken with the user: continuous flow (a stadium may be split across
depots), whole-truck packing (⌈volume/90⌉), uncapacitated depots (UFLP).

---

## 4. Part II — the model in plain words

A **two-stage stochastic program** on the **Round of 32** (16 matches, 28 June
– 3 July). Venues and dates are KNOWN; team identities are UNKNOWN → the source
of uncertainty.

**Stage 1 (before results, frozen):** how much **anticipatory** finished
material to pre-print and pre-position per match, BEFORE knowing the teams.
Because we don't know who qualifies, anticipatory printing covers several
candidate teams → an **over-production waste factor** (default 2×).

**Stage 2 (after each matchup, per scenario):** **reactive** local production
+ trucking site→venue, only if the time window allows.

**Time is a hard binary constraint, not in the objective:** a (site, match)
reactive pair is feasible iff `transit_time(site→venue) ≤ window − production`,
where window = match_date − 27 June and production = 1 day (rush).

**The key result (and why "Voie 3"):** several early R32 matches have windows
too short for reactive supply — LA on day +1, plus the Mexican venues and other
early matches. **6 of the 16 matches are FORCED anticipatory.** This turns what
first looked like an infeasibility "bug" into the project's main managerial
insight: those matches *must* be pre-positioned ahead of time, which is exactly
the role of the stage-1 decision. The model arbitrates reactive vs anticipatory
per match/scenario. Result: ~\$302k expected (\$165k stage-1 + \$137k stage-2).

**Uncertainty pipeline:** team strengths come from tournament-winner betting
odds (user screenshots, validated against Opta: Spain ~16.5%, France ~15%,
England ~11%). A Monte-Carlo simulates the 12 groups (strength-weighted
Plackett-Luce ranking), picks the 8 best third-placed teams, maps qualifiers
into the fixed bracket → 50 equiprobable scenarios, each fixing which teams
play each R32 match. See `src/part2_stochastic/scenarios.py`.

---

## 5. The decision log (chronological highlights)

- Demand absent from CSVs → build it; ventilate by 3 keys (capacity / fixed /
  typology) per inventory poste. LED included (central scenario).
- Container payload = **26 t** — not just from the inventory, but verified as
  the real **US road limit** (ISO gross 30.48 t − ~3.7 t tare ≈ 26.7 t payload;
  US road enforcement ~26 t). So 26 t is the realistic binding limit because
  the LED travels onward by road after the port.
- Part I trucking kept simple (⌈vol/90⌉), NOT 3D bin-packing: depot→stadium is
  ~mono-stadium and only ~13–23% of cost; the real packing leverage is the
  maritime FEU (volume+weight), which is where we put the modelling effort.
- LED allowed direct port→stadium (uses the `port_gateway_to_stadium` edges).
- Part II: "all from China" = raw material imported by sea, **printed locally**.
- Stochastic solved as ONE large MILP (deterministic equivalent), 50 scenarios.
- Production cost ~\$50/m² (US large-format market 2026; \$5/ft²), rush
  production 1 day — both web-sourced.
- Storage cost ($0.03/0.08/0.15 per m³/day) is an **assumed scenario** (FIFA
  depot costs not public) → handled by sensitivity, stated openly.

---

## 6. What is solid vs assumed

See `docs/04_assumptions_registry.md` for the full table with three statuses:
✅ externally sourced, 🔶 derived from project data, ⚠️ assumed-with-sensitivity.
Nothing is invented without a justification path.

---

## 7. Guidelines compliance (Prof. Gallay's brief)

The course brief asks for: an optimisation model (VRP/FLP/packing), real data,
motivated assumptions, mathematical formulation, **sensitivity analysis**,
**graphical representations**, **comparison of set-ups**, a **Define-Measure-
Analyze-Improve** structure, **managerial insights**, code in appendix, an
**executive summary**, and a peer review. Every one of these is addressed —
see `docs/08_report_structure.md`. Deliverable deadline was extended (the
original brief said report 26 May / slides 27 May / presentation 28 May).
