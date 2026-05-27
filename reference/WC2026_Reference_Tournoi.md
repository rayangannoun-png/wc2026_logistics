# Référence FIFA World Cup 2026 — Données tournoi pour le projet MGT-530/SLO

> Fichier de référence consolidé pour la modélisation logistique (Part I coût + Part II stochastique time-critical).
> Sources : tirage officiel FIFA (5 déc. 2025) + barrages résolus (mars 2026) + calendriers Sky Sports / NBC Sports / MLS / AOL (mai 2026) + cotes bookmaker (captures utilisateur).
> ⚠️ Les compositions de groupe et le mapping bracket sont **officiels et figés**. Les *résultats* (qui finit 1er/2e/3e) sont **inconnus** → c'est précisément la source d'incertitude de la Part II.

---

## 1. Format du tournoi (rappel structurel)

| Élément | Valeur |
|---|---|
| Équipes | 48 |
| Groupes | 12 groupes de 4 (A → L) |
| Pays hôtes | USA (11 villes), Mexique (3), Canada (2) |
| Dates | 11 juin → 19 juillet 2026 (39 jours) |
| Matchs totaux | 104 |
| Qualifiés knockout | 32 = (2 premiers × 12 groupes) + (8 meilleurs 3es) |
| Premier tour knockout | **Round of 32** (16 matchs) — nouveau, n'existait pas avant 2026 |
| Tours suivants | Round of 16 → Quarts → Demies → Finale |

**Calendrier des phases :**
| Phase | Dates |
|---|---|
| Phase de groupes | 11 – 27 juin |
| **Round of 32** | **28 juin – 3 juillet** |
| Round of 16 | 4 – 7 juillet |
| Quarts | 9 – 11 juillet |
| Demies | 14 – 15 juillet |
| 3e place | 18 juillet |
| Finale (MetLife, NY/NJ) | 19 juillet |

> Note Part II : la fenêtre time-critical = entre la fin des poules (27 juin) et chaque match du Round of 32 (28 juin – 3 juillet). Soit **1 à 6 jours** selon le match. À partir du Round of 16, tout se joue aux USA uniquement.

---

## 2. Les 12 groupes (composition officielle figée)

> Force = probabilité normalisée dérivée des cotes "vainqueur du tournoi" (bookmaker, marge retirée). Sert de proxy de force d'équipe pour la simulation.

| Groupe | Équipes (force %) |
|---|---|
| **A** | Mexique (0.40), Afrique du Sud (0.10), Corée du Sud (0.41), Rép. Tchèque (0.41) |
| **B** | Canada (0.55), Qatar (0.18), Suisse (1.21), Bosnie-H. (0.36) |
| **C** | Brésil (9.10), Maroc (1.52), Haïti (0.04), Écosse (0.73) |
| **D** | États-Unis (1.21), Paraguay (0.61), Australie (0.26), Turquie (1.21) |
| **E** | Allemagne (5.35), Curaçao (0.04), Côte d'Ivoire (0.61), Équateur (1.21) |
| **F** | Pays-Bas (3.64), Japon (1.52), Tunisie (0.18), Suède (1.21) |
| **G** | Belgique (2.02), Égypte (0.18), Iran (0.18), Nouvelle-Zélande (0.07) |
| **H** | Espagne (16.54), Cap-Vert (0.07), Arabie Saoudite (0.18), Uruguay (1.21) |
| **I** | France (15.16), Irak (0.07), Sénégal (1.46), Norvège (2.60) |
| **J** | Argentine (9.10), Algérie (0.36), Autriche (0.61), Jordanie (0.07) |
| **K** | RD Congo (0.18), Portugal (8.27), Ouzbékistan (0.07), Colombie (1.82) |
| **L** | Angleterre (11.37), Croatie (0.91), Ghana (0.30), Panama (0.07) |

> Barrages résolus (mars 2026) : Rép. Tchèque (UEFA D, gr.A), Bosnie-H. (UEFA A, gr.B), Turquie (UEFA C, gr.D), Suède (UEFA B, gr.F), Irak (intercont. 2, gr.I), RD Congo (intercont. 1, gr.K).

---

## 3. Les 16 stades hôtes (avec liens vers les node_id du projet)

| Ville | Stade | node_id (projet) | Pays | Cluster |
|---|---|---|---|---|
| Mexico City | Estadio Azteca | STAD_MEX | Mexique | mexico_central |
| Guadalajara | Estadio Akron | STAD_GDL | Mexique | mexico_west |
| Monterrey | Estadio BBVA | STAD_MTY | Mexique | mexico_north |
| Toronto | BMO Field | STAD_TOR | Canada | canada_east |
| Vancouver | BC Place | STAD_VAN | Canada | canada_west |
| Los Angeles (Inglewood) | SoFi Stadium | STAD_LA | USA | us_west |
| San Francisco (Santa Clara) | Levi's Stadium | STAD_SF | USA | us_west |
| Seattle | Lumen Field | STAD_SEA | USA | us_west |
| Kansas City | Arrowhead Stadium | STAD_KC | USA | us_central |
| Dallas (Arlington) | AT&T Stadium | STAD_DAL | USA | us_central |
| Houston | NRG Stadium | STAD_HOU | USA | us_gulf |
| Atlanta | Mercedes-Benz Stadium | STAD_ATL | USA | us_southeast |
| Miami (Miami Gardens) | Hard Rock Stadium | STAD_MIA | USA | us_southeast |
| Boston (Foxborough) | Gillette Stadium | STAD_BOS | USA | us_northeast |
| Philadelphia | Lincoln Financial Field | STAD_PHI | USA | us_northeast |
| New York/New Jersey (E. Rutherford) | MetLife Stadium | STAD_NY_NJ | USA | us_northeast |

---

## 4. Round of 32 — les 16 matchs (mapping bracket + stade + date)

> ⚠️ Le bracket est **pré-déterminé et figé dès le 27 juin** (fin des poules). FIFA a pré-planifié les 495 combinaisons possibles d'attribution des 8 meilleurs 3es. Aucun tirage après les poules.
> Les **stades et dates sont connus** ; seules les **équipes** dépendent des résultats (→ incertitude Part II).

| Match | Affrontement (positions de groupe) | Stade | node_id | Date |
|---|---|---|---|---|
| 73 | 2e A vs 2e B | SoFi, Los Angeles | STAD_LA | 28 juin |
| 74 | 1er E vs 3e (A/B/C/D/F) | Gillette, Boston | STAD_BOS | 29 juin |
| 75 | 1er F vs 2e C | Estadio BBVA, Monterrey | STAD_MTY | 29 juin |
| 76 | 1er C vs 2e F | NRG, Houston | STAD_HOU | 29 juin |
| 77 | 1er I vs 3e (C/D/F/G/H) | MetLife, New York/NJ | STAD_NY_NJ | 30 juin |
| 78 | 2e E vs 2e I | AT&T, Dallas | STAD_DAL | 30 juin |
| 79 | 1er A vs 3e (C/E/F/H/I) | Estadio Azteca, Mexico City | STAD_MEX | 30 juin |
| 80 | 1er L vs 3e (E/H/I/J/K) | Mercedes-Benz, Atlanta | STAD_ATL | 1 juillet |
| 81 | 1er D vs 3e (B/E/F/I/J) | Levi's, San Francisco | STAD_SF | 1 juillet |
| 82 | 1er G vs 3e (A/E/H/I/J) | Lumen, Seattle | STAD_SEA | 1 juillet |
| 83 | 2e K vs 2e L | BMO Field, Toronto | STAD_TOR | 2 juillet |
| 84 | 1er H vs 2e J | SoFi, Los Angeles | STAD_LA | 2 juillet |
| 85 | 1er B vs 3e (E/F/G/I/J) | BC Place, Vancouver | STAD_VAN | 2 juillet |
| 86 | 1er J vs 2e H | Hard Rock, Miami | STAD_MIA | 2 juillet |
| 87 | 1er K vs 3e (D/E/I/J/L) | Arrowhead, Kansas City | STAD_KC | 3 juillet |
| 88 | 2e D vs 2e G | AT&T, Dallas | STAD_DAL | 3 juillet |

> Note : 14 stades sur 16 accueillent un match du Round of 32 (Dallas et LA en accueillent 2 chacun ; Guadalajara et Philadelphie n'en accueillent pas à ce tour mais sont utilisés ailleurs). Les matchs s'étalent sur 6 jours (28 juin → 3 juillet).

---

## 5. Règle de qualification des "meilleurs 3es"

8 des 12 troisièmes se qualifient, classés par : (1) points, (2) différence de buts, (3) buts marqués, (4) fair-play.
Les 8 qualifiés sont attribués aux matchs des 1ers de groupe selon une **table pré-définie** (les 495 combinaisons), pour éviter que deux équipes du même groupe se recroisent avant les quarts.

> Pour la simulation Part II : une fois qu'on a simulé les 12 classements de groupe, on connaît les 1ers, 2es, et les 12 troisièmes → on prend les 8 meilleurs 3es → on les place dans le bracket selon la table FIFA → on obtient les 16 affiches concrètes (équipe × stade × date).

---

## 6. Mapping bracket complet (pour propager au-delà du Round of 32, si besoin)

Round of 16 (4-7 juillet) :
- M89 = vainqueur M74 vs vainqueur M77 (Philadelphie)
- M90 = vainqueur M73 vs vainqueur M75 (Houston)
- M91 = vainqueur M76 vs vainqueur M78 (New York/NJ)
- M92 = vainqueur M79 vs vainqueur M80 (Mexico City)
- M93 = vainqueur M83 vs vainqueur M84 (Dallas)
- M94 = vainqueur M81 vs vainqueur M82 (Seattle)
- M95 = vainqueur M85 vs vainqueur M86 (?)
- M96 = vainqueur M87 vs vainqueur M88 (?)

> Les deux "pathways" FIFA gardent Espagne (1) / Argentine (2) et France (3) / Angleterre (4) dans des moitiés séparées → ne peuvent se croiser qu'en demie.

---

## 7. Ce qui est CERTAIN vs INCERTAIN (cadrage modélisation Part II)

| Élément | Statut | Rôle dans le modèle |
|---|---|---|
| Stades de chaque match R32 | ✅ certain | Donnée fixe (destination connue) |
| Dates de chaque match R32 | ✅ certain | Contrainte de temps (deadline) |
| Mapping positions→bracket | ✅ certain | Structure fixe |
| Composition des groupes | ✅ certain | Donnée fixe |
| Force des équipes (cotes) | ✅ figée (hypothèse) | Paramètre de simulation |
| **Qui finit 1er/2e/3e** | ❌ **incertain** | **Variable aléatoire → scénarios** |
| **Quelle équipe joue quel match R32** | ❌ **incertain** | **Sortie de la simulation → demande nominative** |

**Insight clé** : les *lieux* et *dates* sont connus ; seules les *identités d'équipes* sont aléatoires. Donc la demande nominative (drapeaux, decals "Pays A vs Pays B") est ce qui ne peut être produit qu'après les résultats — c'est exactement le flux time-critical de la Part II.
