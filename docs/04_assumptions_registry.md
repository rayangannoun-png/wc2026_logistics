# 04 — Assumptions registry

Every assumption has a justification path. Three statuses:
**✅ externally sourced** · **🔶 derived from project data** · **⚠️ assumed scenario (with sensitivity)**

| # | Assumption | Value | Status | Justification |
|---|---|---|---|---|
| 1 | Container payload limit | **26 t** | ✅ | ISO 40ft gross 30.48 t − ~3.7 t tare ≈ 26.7 t payload; US road enforcement ~26 t. LED travels onward by road → road limit binds. (web) |
| 2 | Container interior volume | 67 m³ | ✅ | ISO 40ft standard. |
| 3 | Truck usable volume | 90 m³ | ✅ | US dry-van trailer (16.15×2.5×2.7). Inventory Part E. |
| 4 | Container fill rate | 57% | 🔶 | Inventory anchored conversion (rolls + voids). |
| 5 | LED density | ~0.994 t/m³ | 🔶 | Derived: 1,066 t / 1,072 m³ (inventory Partie G). |
| 6 | Soft density | ~0.46 t/m³ | 🔶 | Derived: 762 t / 1,654 m³ (inventory Partie G). |
| 7 | Production cost | ~\$50/m² | ✅ | US large-format market 2026 (~\$5/ft², multiple sources). Sensitivity \$20/\$50/\$86. |
| 8 | Rush production lead time | 1 day | ✅ | Rush/same-day large-format printing (web). Sensitivity 0/1 day. |
| 9 | Storage cost | \$0.03/0.08/0.15 per m³/day | ⚠️ | FIFA depot storage costs not public → assumed scenario; covered by low/base/high sensitivity. |
| 10 | Anticipatory waste factor | 2× | ⚠️ | Pre-printing for ~2 candidate teams; sensitivity 1×/2×/3×. |
| 11 | Raw-material wait horizon | 30 days | ⚠️ | Storage horizon before knockout; assumed. |
| 12 | Nominative material/match | 275 m² | ✅ | Inventory Part D.2 (flags 75 + decals 150 + backdrops 50). |
| 13 | Part I storage | excluded | 🔶 | Cat-1 transits, not stored long term. Decision. |
| 14 | LED routing | direct port→stadium | 🔶 | Data README: direct flows for oversized/pre-kitted shipments; 1 system/stadium. |
| 15 | Depot capacity | uncapacitated (UFLP) | 🔶 | `capacity_proxy_m3` empty in CSV → UFLP (course Session 6). |
| 16 | Origin | all from China + local print | 🔶 | Inventory assumption; raw imported, printed locally (Part II). |
| 17 | Scenario count | 50, equiprobable | ⚠️ | Monte-Carlo sample size; balance richness vs solve time. |
| 18 | Demand ventilation | 3 keys (cap/fixed/typology) | 🔶 | Per-poste physics; reconciles to 2,726 m³ / 1,828 t. |
| 19 | Team strengths | winner odds, normalised | ✅ | User betting screenshots; validated vs Opta. Strength proxy. |
| 20 | Ports/depots/edges/costs | as given | ✅ | Project CSVs. |

## How to talk about these in the report

- ✅ → cite the source (see `docs/09_sources.md`).
- 🔶 → show the derivation (a line of arithmetic from project data).
- ⚠️ → state openly it is an assumed scenario and show the **sensitivity**
  range. This is *more* rigorous than pretending a number is sourced.
