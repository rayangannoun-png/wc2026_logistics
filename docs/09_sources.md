# 09 — Source registry (entire project)

Every source used across the **whole project** (this design conversation + the
earlier inventory/cost conversation + web research), with **what each one
justifies**. Status: ✅ external · 🔶 derived · ⚠️ assumed.

---

## A. Tournament structure & schedule

| Source | Justifies | Status |
|---|---|---|
| FIFA official draw (5 Dec 2025) + playoffs resolved (Mar 2026) | 12 groups, 48 teams, resolved playoff winners (Czechia, Bosnia, Turkey, Sweden, Iraq, DR Congo) | ✅ |
| MLS / NBC Sports / Sky Sports / AOL / Bleacher Report schedules (May 2026) | R32 bracket mapping (which group position plays where), venues, dates | ✅ |
| Britannica / StadiumDB / Soccergraph | format (16 stadiums, 104 matches, 39 days), stadium capacities | ✅ |
| `reference/WC2026_Reference_Tournoi.md` | consolidated tournament reference (groups, bracket, schedule) | 🔶 |

## B. Team strengths (Part II uncertainty)

| Source | Justifies | Status |
|---|---|---|
| Bookmaker winner odds (user screenshots, 27 May 2026) | strength proxy for all 48 teams (normalised, margin removed) | ✅ |
| Opta supercomputer (theanalyst.com, SI, beIN) | cross-check of strengths (Spain ~17%, France ~14%, England ~12%) | ✅ |

## C. Branding inventory (demand) — from the earlier conversation

| Source | Justifies | Status |
|---|---|---|
| The Look Company — Qatar 2022 case study | aggregate quantities (905,000 m², 87 km scrim, 21,693 street banners, 3,300 flags, 1,000 wayfinding, 151 vehicles). NOTE: per-category breakdown is NOT public → our split is a reasoned reconstruction | ✅ (aggregates) / 🔶 (split) |
| bluemedia Super Bowl LIII Atlanta (Yahoo/bluemedia) | building-wrap m²/stadium ratio (~9,300 m²) | ✅ |
| CSM Live / Premier League (cityam.com) | seat-cover ratio (~3,000 m²/stadium) | ✅ |
| JYVISIONS (jyvisions.com) | LED perimeter = ~1 40ft container/stadium | ✅ |
| ARC Supplies / Aarongraphics | roll dimensions → anchored volume conversion (0.00056 m³/m²) | ✅ |
| Camden Council "Look" spec sheet | material weights (scrim 115 g/m², flag 110 g/m²) | ✅ |
| Tampa Printing | vinyl 13oz weight (4.03 m² = 2.72 kg → 0.67 kg/m²) | ✅ |
| TecMaschin | LED cabinet weight (~46 kg/panel) → LED density | ✅ |
| Sports Business Journal / Facilities Dive (Drew Bryant, Elevate) | brand scrubbing ~2,000 elements at Mercedes-Benz Stadium | ✅ |
| The Mirror / The Athletic | FIFA "clean stadium" clause 6.4.ii | ✅ |
| Tender Host City Cologne, Euro 2024 (business.gov.uk) | fan-zone PVC fence banner quantities (reference) | ✅ |
| Coliseum (coliseum-online.com) | 2026 providers (The Look Company + Wasserman Live) | ✅ |
| `reference/Reconstitution_Inventaire_WC2026.md` | the demand totals (2,726 m³ / 1,828 t) and per-poste figures | 🔶 |
| `reference/Reconstitution_Inventaire_Qatar2022.md` | the Qatar baseline the 2026 figures extrapolate from | 🔶 |
| `reference/Inventaire_Branding_FIFA_Types_Produits.md` | product nomenclature + transport profiles (LCL compatibility) | ✅/🔶 |

## D. Cost & logistics parameters

| Source | Justifies | Status |
|---|---|---|
| Project CSVs (ports/depots/edges) | FCL/LCL rates, customs, handling, depot costs, distances, transit times, border costs | ✅ |
| Web: 40ft container weight (FreightAmigo, Conexwest, Aztec, etc.) | 26 t payload (ISO gross 30.48 t − tare; US road ~26 t) | ✅ |
| Web: large-format printing cost (unanswered.io, costhack, NorthCoast, etc.) | production cost ~\$50/m² (\$3–8/ft², 2026) | ✅ |
| Web: rush/same-day printing (Signs NYC, Design One, etc.) | production lead time 1 day (rush) | ✅ |
| `storage_scenarios.csv` (basis: not public) | storage \$0.03/0.08/0.15 per m³/day | ⚠️ |
| US dry-van trailer dims | truck 90 m³ | ✅ |

## E. Course methodology

| Source | Justifies | Status |
|---|---|---|
| `reference/SLO_Cours_Knowledge_Base.md` | OR-Tools patterns, MILP/facility-location/packing/stochastic formulations | ✅ |

---

### Honesty notes (state these in the report)

- The Look Company does **not** publish a per-category m² breakdown; our
  inventory split is a transparent reconstruction anchored on the public
  aggregates.
- Storage costs and the anticipatory waste factor are assumed; we cover them
  with sensitivity ranges rather than claiming a source.
- Betting odds are used as a **strength proxy**, turned into qualification
  frequencies by Monte-Carlo — not as direct qualification probabilities.
