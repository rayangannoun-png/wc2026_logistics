# Reconstitution de l'inventaire de branding — FIFA World Cup 2026
## Extrapolation depuis Qatar 2022 (méthodologie ancrée m² → m³ → FEUs)

> Projet MGT-530 (FIFA World Cup 2026 — Venue Signage Distribution)
> Objectif : estimer le volume de branding/signalétique à distribuer pour la CdM 2026, en partant de la reconstitution ancrée de Qatar 2022.
> Hypothèses : **tout vient de Chine** (LED inclus) ; périmètre = **stades + précinct immédiat** (city dressing des 16 villes exclu, comme pour Qatar).

---

## SYNTHÈSE EXÉCUTIVE (à lire en premier)

### Les chiffres clés

| Métrique | Qatar 2022 | **CdM 2026** | Ratio |
|---|---|---|---|
| Stades | 8 | 16 | ×2 |
| Surface de branding (scope stade+précinct) | ~640,000 m² | **~1,480,000 m²** | ×2.3 |
| Volume total | ~1,262 m³ | **~2,726 m³** | ×2.2 |
| Poids total | — | **~1,749 t** | — |
| FEUs (par volume) | ~28 | **~61** | ×2.2 |
| FEUs (poids LED inclus) | — | **~77** ⚠️ | — |
| Palettes (entrepôt) | — | **~814** | — |

### Les 5 enseignements pour la modélisation

1. **Périmètre** : on garde stades + précinct (~71% des m²), city dressing des 16 villes exclu (comme Qatar). Soit ~88,000 m²/stade.

2. **Le LED domine et se comporte différemment** : 39% du volume, mais **saturé en POIDS** (pas en volume). Il fait passer le total de ~61 à ~77 FEUs. Si exclu (loué localement) → ~37 FEUs propres, tous volume-driven.

3. **Le brand scrubbing est le poste NOUVEAU de 2026** : masquer le branding NFL existant (~2,000 éléments/Mercedes-Benz). Faible en volume (2.5%) mais médiatiquement central et spécifique à 2026.

4. **Split temporel = 99.8% / 0.2%** : presque tout est générique CdM (Cat 1, planifiable par mer). Seuls les drapeaux/decals des 24 affiches knockout (Cat 2, <1 FEU) attendent les résultats → flux dynamique via site de production USA.

5. **Packing** : ~90% du volume est souple/gerbable/LCL-OK. Seuls le LED (FCL, lourd, fragile) et les mâts (>3m) imposent du FCL/flat-rack → cohérent avec l'approche hybride FCL+LCL.

### Fourchette finale défendable

| Scénario | Volume | FEUs |
|---|---|---|
| Bas (LED exclu, taille +0%) | ~1,500 m³ | ~33 |
| **Central (LED inclus, taille +10%)** | **~2,726 m³** | **~61 (volume) / ~77 (poids)** |
| Haut (LED inclus, scrubbing 100k, taille +20%) | ~3,100 m³ | ~69-85 |

### Structure du document

- **Partie A** — État des lieux Qatar 2022 vs 2026 (sourcé)
- **Partie B** — Reconstitution chiffrée 2026 poste par poste (m² → m³ → FEUs)
- **Partie C** — Synthèse et comparaison + analyse de sensibilité
- **Partie D** — Split temporel Cat 1 (planifiable) / Cat 2 (time-critical)
- **Partie E** — Dimensions de packing (colis unitaire + palettisation + gabarit)
- **Partie F** — Nombre de palettes & dimensionnement entrepôt
- **Partie G** — Poids par catégorie & saturation volume vs poids

---

## PARTIE A — État des lieux : Qatar 2022 vs CdM 2026

### A.1 Tableau comparatif structurel

| Critère | Qatar 2022 | CdM 2026 | Source |
|---|---|---|---|
| Stades | 8 | **16** (×2) | Britannica ; StadiumDB |
| Matchs | 64 | **104** (+62%) | Britannica ; FIFA |
| Équipes | 32 | **48** (+50%) | Britannica ; Sky Sports |
| Villes hôtes | 1 (Doha) | **16 villes / 3 pays** (USA 11, Mexique 3, Canada 2) | Britannica |
| Étendue géographique | Tous stades dans ~35 miles du centre de Doha | **>4,000 miles** (Vancouver → Boston) | matchbingo / The Athletic |
| Durée | ~29 jours | **39 jours** | Britannica |
| Type de stades | Neufs / vierges, construits pour FIFA | **Stades NFL/existants** avec branding commercial | Coliseum ; SBJ |
| Prestataires branding | The Look Company | **The Look Company + Wasserman Live** (ex-bluemedia) | Coliseum |

### A.2 Les facteurs qui font MONTER le volume 2026

**① Le nombre de stades (×2) — facteur direct**
16 stades au lieu de 8. C'est le multiplicateur de base le plus évident.

**② La taille des stades (NFL > Qatar)**
Les stades 2026 sont en moyenne plus grands que les stades qataris. Capacités 2026 (source : FIFA ticketing / StadiumDB / Soccergraph) :

| Stade | Ville | Capacité | Toit |
|---|---|---|---|
| MetLife (NY/NJ) | New York | ~82,500 | Ouvert |
| Estadio Azteca | Mexico City | ~72,700 | Ouvert |
| AT&T (Dallas) | Dallas | ~80,000–94,000 | Rétractable |
| Arrowhead | Kansas City | ~76,400 | Ouvert |
| NRG | Houston | ~71,500 | Rétractable |
| Mercedes-Benz | Atlanta | ~71,000 | Rétractable |
| SoFi (LA) | Los Angeles | ~70,000 | Canopée fixe ETFE |
| Levi's | San Francisco | ~69,400 | Ouvert |
| Lumen Field | Seattle | ~69,000 | Partiel |
| Gillette | Boston | ~68,800 | Ouvert |
| Lincoln Financial | Philadelphie | ~69,000 | Ouvert |
| Hard Rock | Miami | ~65,300 | Canopée |
| Estadio Akron | Guadalajara | ~48,000 | Ouvert |
| Estadio BBVA | Monterrey | ~53,500 | Ouvert |
| BC Place | Vancouver | ~54,500 | Dôme rétractable |
| BMO Field | Toronto | ~44,300 | Ouvert |

Moyenne 2026 ≈ **~67,000 places/stade**. Les stades Qatar allaient de 40,000 à 80,000 (moyenne ~45,000–50,000 hors Lusail). → Stades 2026 globalement **plus grands**, donc plus de surface intérieure (concourses, tunnels, suites, vomitoires) à habiller.

**③ Le brand scrubbing / "clean site" — LE poste UNIQUE à 2026** ⭐
C'est la grande différence. Les stades qataris étaient neufs et vierges. Les stades NFL 2026 sont saturés de branding commercial existant qu'il faut **couvrir**.

> Clause 6.4.ii d'un contrat de ~100 pages signé par chaque stade : interdiction de toute identification commerciale "sur les tribunes, tableaux de score, sièges, dossiers de sièges, horloges, tenues du personnel, clôtures, ou ailleurs à l'intérieur, autour et dans l'espace aérien du stade" autre que celle installée par FIFA. (Source : The Mirror / The Athletic ; Coliseum)

Chiffre concret : **~2,000 éléments à couvrir/retirer pour le seul Mercedes-Benz Stadium** (71,000 places). (Source : Sports Business Journal / Facilities Dive, citant Drew Bryant d'Elevate)

15 des 16 stades ont des contrats de naming + logos sponsors à masquer (seul BC Place échappe). → **Poste de matériel de masquage entièrement nouveau**, qui n'existait pas au Qatar.

**④ Plus d'équipes / matchs**
48 équipes (vs 32) → plus de drapeaux nationaux, plus de team branding, plus de matchs = plus d'usure/remplacement.

### A.3 Les facteurs qui font BAISSER (ou neutralisent) le volume par stade

**⑤ City dressing dispersé sur 16 villes → hors scope**
À Doha, une seule ville ultra-dense. En 2026, le city dressing est géré ville par ville (cf. modèle tender Cologne Euro 2024). Comme pour Qatar, on **l'exclut du scope** stade+précinct. Ça ne fait donc pas monter notre chiffre.

**⑥ Réversibilité (config NFL à restaurer)**
Les stades doivent revenir en config NFL après le tournoi → branding plutôt temporaire/amovible que collé en permanence. Peut légèrement limiter certains postes (decals permanents).

### A.4 Synthèse de l'impact

| Facteur | Direction | Ampleur estimée |
|---|---|---|
| ① 2× stades | ⬆️⬆️ | Fort (base ×2) |
| ② Stades plus grands | ⬆️ | Moyen (+15-25%/stade) |
| ③ Brand scrubbing NFL | ⬆️ | Nouveau poste net |
| ④ +équipes / +matchs | ⬆️ | Faible-moyen |
| ⑤ City dressing dispersé | neutre | Hors scope (comme Qatar) |
| ⑥ Réversibilité | ⬇️ | Faible |

**Intuition avant calcul détaillé** : volume 2026 ≈ **2.5–3.5× Qatar** (scope stade+précinct) → ordre de grandeur **~3,000–4,000 m³**, **~65–90 FEUs**. À affiner poste par poste dans la Partie B.

---

## PARTIE B — Reconstitution chiffrée 2026

### B.0 Principe

On reconstruit poste par poste, comme pour Qatar, en gardant les **3 niveaux de confiance** (🟢🟡🔴) et la **même méthode de conversion ancrée** (rouleau ARC → 0.00056 m³/m² pur, ÷0.57 remplissage conteneur). On ajoute un poste **brand scrubbing** propre à 2026.

Périmètre : **16 stades + précinct**, city dressing des villes exclu (comme Qatar).

### B.1 Calibrage par rapport à Qatar

Référence Qatar (scope stade+précinct) = **~80,000 m²/stade** sur 8 stades.
Pour 2026 on ajuste ce ratio par stade selon 2 effets :
- **Taille** : stades 2026 ~67,000 places en moyenne vs ~50,000 Qatar → +~15% de surface intérieure/façade.
- **Réversibilité** : léger frein sur le permanent (−5%).
- Effet net taille ≈ **+10%/stade** → **~88,000 m²/stade** (hors brand scrubbing).

### B.2 ÉTAPE 1 — m² par poste (hors brand scrubbing)

| Poste | Méthode | m²/stade | × 16 stades | Niveau |
|---|---|---|---|---|
| Fence scrim (précinct) | Qatar 15,000 m²/stade × 1.0 | 15,000 | 240,000 | 🟢 |
| Building wraps (façades) | bluemedia ~9,300 m²/stade × 1.1 (stades NFL plus grands) | 10,200 | 163,000 | 🟡 |
| Seat covers / sections | Qatar 3,000 × 1.15 (plus de sièges) | 3,450 | 55,000 | 🟡 |
| Pitch-side imprimé | ~700 m²/stade | 700 | 11,000 | 🟡 |
| Wayfinding précinct | ~350 m²/stade | 350 | 5,600 | 🟢 |
| Vehicle wraps | ~470 m²/stade (≈ Qatar 7,550/16) | 470 | 7,550 | 🟢 |
| Intérieur stades (résidu) | ~58,000 m²/stade (Qatar 50,750 × 1.15) | 58,000 | 928,000 | 🔴 |
| **Sous-total hors scrubbing** | | **~88,000** | **~1,410,000 m²** | |

### B.3 ÉTAPE 1bis — Le poste NOUVEAU : Brand scrubbing 🆕

**Ancrage** : ~2,000 éléments à couvrir pour Mercedes-Benz Stadium (gros stade très brandé). Stades récents (SoFi) = charge "plus légère".

**Hypothèse de surface par élément couvert** : un "élément" va d'un petit logo de siège (~0.5 m²) à une enseigne de concourse ou un panneau de scoreboard (plusieurs m²). On retient une **moyenne pondérée ~3 m²/élément** (mix de petits logos nombreux + quelques grandes enseignes).

| Type de stade | Nb stades | Éléments/stade | Surface masquage/stade | Source |
|---|---|---|---|---|
| Anciens, très brandés (Mercedes-Benz, Arrowhead, NRG, AT&T...) | ~8 | ~2,000 | ~6,000 m² | SBJ / Facilities Dive (2,000 éléments MBS) |
| Récents / moins brandés (SoFi, Levi's, MetLife) | ~5 | ~1,000 | ~3,000 m² | "charge plus légère" (Facilities Dive) |
| Mexique/Canada (Azteca, BBVA, Akron, BC Place, BMO) | ~3 (BC Place exempté naming) | ~700 | ~2,100 m² | Moins de naming NFL agressif |

Estimation totale brand scrubbing :
```
8 stades × 6,000 m²  = 48,000 m²
5 stades × 3,000 m²  = 15,000 m²
3 stades × 2,100 m²  =  6,300 m²
──────────────────────────────
≈ 69,000 m² de matériel de masquage
```

> 🔴 Poste très incertain : la conversion "élément → m²" est une hypothèse. Fourchette défendable : **40,000–100,000 m²** selon la surface moyenne retenue par élément (2 à 4 m²).

### B.4 Récapitulatif ÉTAPE 1 (m²)

| Catégorie | m² | % |
|---|---|---|
| Postes classiques (16 stades) | ~1,410,000 | 95% |
| Brand scrubbing (nouveau) | ~69,000 | 5% |
| **TOTAL scope 2026** | **~1,480,000 m²** | 100% |

> Pour comparaison : Qatar scope = ~640,000 m². Ratio 2026/Qatar = **~2.3×** en surface.

### B.5 ÉTAPE 2 — Conversion m² → m³

Même méthode ancrée. Matériaux souples : `(m² × 0.00056) ÷ 0.57`.

| Catégorie | m² | Volume conteneur (m³) |
|---|---|---|
| Fence scrim | 240,000 | 236 |
| Building wraps | 163,000 | 160 |
| Seat covers | 55,000 | 54 |
| Pitch-side | 11,000 | 11 |
| Wayfinding (souple part) | 5,600 | 6 |
| Vehicle wraps | 7,550 | 7 |
| Intérieur (résidu souple) | 928,000 | 912 |
| Brand scrubbing (vinyl/fabric) | 69,000 | 68 |
| **Sous-total souple** | 1,479,150 | **~1,454 m³** |

**Structures rigides + LED** (scalées ×2 vs Qatar, ajustées) :

| Structure | Volume | Base |
|---|---|---|
| LED perimeter boards | 16 stades × 67 m³ = **1,072 m³** | JYVISIONS (1 système = 1 conteneur 40ft/stade) |
| Wayfinding totems (alu) | ~140 m³ | ~2× Qatar |
| Mâts / structures précinct | ~60 m³ | ~2× Qatar |
| **Sous-total rigide + LED** | **~1,272 m³** | |

### B.6 Récapitulatif ÉTAPE 2 (m³)

| Type | Volume |
|---|---|
| Matériaux souples (rouleaux) | ~1,454 m³ |
| Structures rigides + LED | ~1,272 m³ |
| **VOLUME TOTAL 2026 (scope stade+précinct, tout de Chine)** | **~2,726 m³** |

### B.7 ÉTAPE 3 — Conversion m³ → FEUs

```
Volume total : 2,726 m³
÷ 45 m³/FEU (remplissage réaliste)
─────────────────
= ~61 FEUs
```

| Hypothèse remplissage | FEUs |
|---|---|
| Conservateur (33 m³/FEU) | ~83 FEUs |
| Réaliste (45 m³/FEU) | ~61 FEUs |
| Optimiste (60 m³/FEU) | ~45 FEUs |

---

## PARTIE C — Synthèse et comparaison

### C.1 Résultat 2026 vs Qatar 2022

| Métrique | Qatar 2022 | CdM 2026 | Ratio |
|---|---|---|---|
| Stades | 8 | 16 | ×2 |
| m² de branding (scope) | ~640,000 | ~1,480,000 | ×2.3 |
| Volume total | ~1,262 m³ | **~2,726 m³** | ×2.2 |
| Nombre de FEUs | ~28 | **~61** (45-83) | ×2.2 |
| Par stade | ~158 m³, ~3.5 FEUs | ~170 m³, ~3.8 FEUs | +8%/stade |

> Le ratio ~2.2× (pas tout à fait ×2.3 des m²) s'explique : le LED scale en ×2 pile (1 système/stade), ce qui tire le ratio volume vers ×2.

### C.2 Décomposition du volume 2026

| Poste | Volume | % | Confiance |
|---|---|---|---|
| LED perimeter | 1,072 m³ | 39% | 🟡 ancré |
| Intérieur stades (souple) | 912 m³ | 33% | 🔴 hypothèse |
| Fence scrim | 236 m³ | 9% | 🟢 calculable |
| Building wraps | 160 m³ | 6% | 🟡 ratio bluemedia |
| Brand scrubbing 🆕 | 68 m³ | 2.5% | 🔴 nouveau, incertain |
| Autres (seat, totems, pitch, mâts, véhicules) | 278 m³ | 10% | mixte |

### C.3 Les leviers d'incertitude majeurs (analyse de sensibilité 2026)

1. **LED (39%)** : si exclu (loué localement), le total tombe de ~2,726 à ~1,654 m³ (~37 FEUs). Plus gros levier, comme pour Qatar.
2. **Intérieur stades (33%)** : pur résidu/hypothèse, amplifié par le facteur taille ×1.15.
3. **Brand scrubbing (2.5% en volume, mais nouveau)** : faible en volume mais c'est le poste le plus médiatisé/spécifique à 2026. Fourchette 40,000-100,000 m².
4. **Facteur taille (+10%/stade)** : si on prend +0% ou +20%, le total bouge de ±~150 m³.

### C.4 Fourchette finale défendable

| Scénario | Volume | FEUs |
|---|---|---|
| Bas (LED exclu, taille +0%) | ~1,500 m³ | ~33 |
| **Central (LED inclus, taille +10%)** | **~2,726 m³** | **~61** |
| Haut (LED inclus, scrubbing 100k, taille +20%) | ~3,100 m³ | ~69 |

---

## PARTIE D — Split temporel : Catégorie 1 (planifiable) vs Catégorie 2 (time-critical)

### D.0 Le critère de classement (binaire, simple à modéliser)

Chaque produit reçoit UN flag selon une seule question :

> **« Ce produit peut-il être posé au stade SANS connaître l'identité des équipes du match ? »**

| Réponse | Catégorie | Flux logistique |
|---|---|---|
| **OUI** — générique CdM, indépendant de l'affiche | **Cat 1** | Chine → port → entrepôt → tri → **stade** |
| **NON** — dépend de quelle équipe joue | **Cat 2** | Chine → port → entrepôt → **attente** → (résultats) → **site de production** → finition → stade |

**Principe** : 1 produit = 1 flux = 1 catégorie (pas de split en %). Ce qui classe un produit en Cat 2 n'est pas sa matière mais le fait qu'il **ne peut pas rejoindre le stade tant que l'affiche knockout n'est pas connue**.

### D.1 Classement par produit

| Produit | m² (2026) | Cat | Justification |
|---|---|---|---|
| Fence scrim | 240,000 | **1** | Générique CdM/ville, connu à l'avance |
| Building wraps | 163,000 | **1** | Branding tournoi/ville hôte, générique |
| Brand scrubbing | 69,000 | **1** | Logos NFL à couvrir connus dès la signature |
| Seat covers | 55,000 | **1** | Génériques CdM |
| Pitch-side imprimé | 11,000 | **1** | Générique (sponsors FIFA fixes) |
| Wayfinding précinct | 5,600 | **1** | Générique (plans, portes) |
| Vehicle wraps | 7,550 | **1** | Génériques officiels |
| Intérieur stades | 928,000 | **1** | Générique CdM (concourses, tunnels, suites) |
| **— Sous-total Cat 1 —** | **~1,479,150** | | **planifiable, par mer, posé pour tout le tournoi** |
| Drapeaux nationaux (knockout) | ~1,800 | **2** | Dépend des qualifiés — tissu importé, imprimé au site prod |
| Decals match-specific (entrées, line-ups, mixed zone) | ~3,600 | **2** | « Pays A vs Pays B » — connu 48-96h avant |
| Press backdrops team-specific | ~1,200 | **2** | Drapeaux/noms des 2 équipes de l'affiche |
| **— Sous-total Cat 2 —** | **~6,600** | | **time-critical, finition USA, 24 matchs knockout** |

### D.2 Détail du calcul Cat 2 (team-specific knockout)

Base : **24 matchs knockout** (Round of 32 → finale).

| Poste | Par match | × 24 matchs | Profil |
|---|---|---|---|
| Drapeaux nationaux (2 équipes) | ~75 m² | 1,800 m² | Tissu importé Chine, sur-imprimé USA |
| Decals match-specific | ~150 m² | 3,600 m² | Vinyl imprimé USA |
| Press backdrops | ~50 m² | 1,200 m² | Tissu/vinyl imprimé USA |
| **Total/match** | **~275 m²** | **~6,600 m²** | |

> Note : les matériaux bruts (tissu drapeau vierge, vinyl) viennent quand même de Chine. Mais comme le produit entier suit le flux 2 (attente → production → stade), tout son volume est compté en Cat 2.

### D.3 Volumes par catégorie (m² → m³ → FEUs)

Conversion souple : `(m² × 0.00056) ÷ 0.57`. LED et structures = Cat 1 (génériques).

| Catégorie | m² | Volume souple (m³) | + Rigide/LED (m³) | Volume total (m³) | FEUs (÷45) |
|---|---|---|---|---|---|
| **Cat 1 (planifiable)** | 1,479,150 | ~1,454 | ~1,272 | **~2,726 m³** | **~61** |
| **Cat 2 (time-critical)** | 6,600 | ~6.5 | 0 | **~6.5 m³** | **<1** |
| **TOTAL** | 1,485,750 | ~1,460 | ~1,272 | **~2,732 m³** | **~61** |

### D.4 Lecture pour la modélisation

| | Cat 1 — Planifiable | Cat 2 — Time-critical |
|---|---|---|
| **Volume** | ~2,726 m³ (~61 FEUs) | ~6.5 m³ (fraction de FEU) |
| **% du volume total** | **99.8%** | **0.2%** |
| **Quand** | Mois à l'avance | 48-96h avant chaque match knockout |
| **Origine production** | Chine (fini) | Chine (brut) + finition USA |
| **Flux** | port → entrepôt → stade | port → entrepôt → attente → prod → stade |
| **Objectif d'optim** | Coût / CO2 (pas de contrainte temps) | Temps (fenêtre serrée) |
| **Correspondance rapport** | Part I (LRP déterministe) | Part II (knockout dynamique) |

### D.5 L'insight clé

**Le volume Cat 2 est minuscule (~0.2%) mais c'est lui qui porte toute la complexité du modèle dynamique.** L'essentiel du branding (99.8%) est générique CdM et peut être posé pour tout le tournoi dès la phase de poules. Seule une infime fraction — les drapeaux et decals des affiches knockout — doit attendre les résultats et suivre le flux de production de dernière minute.

> ⚠️ Ce déséquilibre est **logique et attendu** : un stade habillé aux couleurs « FIFA World Cup 26 » ne change pas selon qui joue ; seuls les éléments nominatifs (drapeaux, line-ups) sont match-specific. C'est exactement pourquoi le rapport sépare Part I (gros volume, planifiable, optim coût/CO2) et Part II (petit volume, time-critical, optim délai).

### D.6 Nuance pour la robustesse du modèle

Si tu veux gonfler un peu la Cat 2 pour stress-tester le flux dynamique, deux leviers honnêtes :
1. **Inclure l'usure** : remplacer ~5-10% du générique des stades knockout (matériel abîmé après les poules) ferait passer la Cat 2 à ~50-100 m³ (~1-2 FEUs).
2. **Élargir le team-specific** : si chaque match knockout nécessite plus de signalétique nominative (fan zones team-specific, etc.), on peut monter à ~500 m²/match → ~12,000 m² (~12 m³).
Mais dans le scénario central réaliste, **Cat 2 reste sous 1 FEU.**

---

## PARTIE E — Dimensions de packing par produit (conteneur & camion)

> Objectif : passer du volume agrégé aux **dimensions physiques d'emballage** de chaque produit, pour modéliser le calage réel dans un conteneur 40ft (FCL) ou une remorque (camion), et pas seulement le volume théorique.

### E.0 Références de packing (sources)

| Élément | Dimension | Source |
|---|---|---|
| Palette US GMA (standard Amérique du Nord) | 1.22 × 1.02 m, 2 côte à côte = remorque | Ace Pallet / Freightquote |
| Hauteur palette gerbable | 1.5–1.8 m (load height 60-72") | John Maye Co / Interwf |
| Conteneur 40ft (FEU) | 12.03 × 2.35 × 2.39 m (int.), ~67 m³ | Standard ISO |
| Remorque camion (dry van US) | 16.15 × 2.50 × 2.70 m, ~90 m³ utile | Modèle MGT-530 (cap. 90 m³) |
| Panneau LED perimeter | 1.60 × 0.90 × 0.098 m, 4/flight case | JYVISIONS |
| Flight case LED (3 displays) | 0.54 × 1.69 × 1.285 m | TecMaschin |
| Limite gabarit LCL | 3.0 × 2.0 × 1.78 m, ≤1,000 kg/pièce | Rapport MGT-530 |

### E.1 Dimensions du colis unitaire par produit

| Produit | Forme d'emballage | Dimensions unitaires (L×l×H ou L×Ø) | Volume colis | Poids approx. |
|---|---|---|---|---|
| Fence scrim | Rouleau | 1.60 m × Ø0.25 m | 0.079 m³ | ~18 kg |
| Building wraps | Rouleau grand format | 3.20 m × Ø0.30 m | 0.226 m³ | ~50 kg |
| Seat covers | Carton plat / ballot | 1.20 × 0.80 × 0.40 m | 0.384 m³ | ~25 kg |
| Pitch-side imprimé | Rouleau | 1.60 × Ø0.20 m | 0.050 m³ | ~12 kg |
| Vinyl intérieur / decals | Rouleau | 1.55 × Ø0.20 m | 0.049 m³ | ~13 kg |
| Vehicle wraps | Rouleau | 1.55 × Ø0.18 m | 0.039 m³ | ~10 kg |
| Wayfinding totems (alu) | Caisse plate démontée | 2.20 × 0.80 × 0.15 m | 0.264 m³ | ~35 kg |
| Mâts drapeaux (RFT) | Tube long | 3.50 × Ø0.12 m | 0.040 m³ | ~8 kg |
| LED perimeter (panneau) | Flight case (×4 panneaux) | 1.70 × 1.05 × 0.45 m | 0.803 m³ | ~210 kg |
| Brand scrubbing (covers) | Rouleau / ballot | 2.00 × Ø0.30 m | 0.141 m³ | ~30 kg |
| **Cat 2 — Drapeaux nationaux** | Rouleau tissu | 1.20 × Ø0.15 m | 0.021 m³ | ~4 kg |
| **Cat 2 — Decals match** | Rouleau vinyl | 1.55 × Ø0.18 m | 0.039 m³ | ~10 kg |
| **Cat 2 — Press backdrops** | Caisse pliée | 1.20 × 0.60 × 0.30 m | 0.216 m³ | ~15 kg |

### E.2 Unité de manutention (palettisation)

Comment chaque produit se groupe sur palette US (1.22 × 1.02 m) pour le chargement conteneur/camion :

| Produit | Conditionnement palette | Colis/palette | Dim. palette chargée (H) | Volume palette |
|---|---|---|---|---|
| Fence scrim | Rouleaux couchés, croisés | ~40 rouleaux | 1.60 m | ~2.0 m³ |
| Building wraps | Rouleaux longs (dépassent) | ~12 rouleaux | 3.20 m (hors gabarit H) | ~2.7 m³ |
| Seat covers | Cartons empilés | ~10 cartons | 1.60 m | ~2.0 m³ |
| Vinyl intérieur/decals | Rouleaux verticaux | ~60 rouleaux | 1.60 m | ~2.0 m³ |
| Wayfinding totems | Caisses gerbées | ~8 caisses | 1.40 m | ~1.7 m³ |
| Mâts drapeaux | Fagots de tubes | ~50 mâts | 3.50 m (hors gabarit L) | ~0.6 m³/fagot |
| LED perimeter | Flight cases gerbés | 2 cases | 0.90 m | ~1.6 m³ |
| Brand scrubbing | Rouleaux/ballots | ~20 unités | 1.60 m | ~2.0 m³ |

### E.3 Contraintes de gabarit (ce qui pilote le packing réel)

| Produit | Compatible LCL ? | Gerbable ? | Longueur >3m ? | Fragile ? | Profil camion |
|---|---|---|---|---|---|
| Fence scrim | ✅ | ✅ | ❌ | ❌ | Idéal, dense |
| Building wraps | ⚠️ (rouleaux >3m) | ⚠️ | ⚠️ 3.2m | ❌ | Rouleaux longs à plat |
| Seat covers | ✅ | ✅ | ❌ | ❌ | Idéal |
| Pitch-side imprimé | ✅ | ✅ | ❌ | ❌ | Idéal |
| Vinyl intérieur/decals | ✅ | ✅ | ❌ | ❌ | Idéal |
| Vehicle wraps | ✅ | ✅ | ❌ | ❌ | Idéal |
| Wayfinding totems | ⚠️ (selon dim.) | ✅ | ❌ | ⚠️ | Caisses gerbables |
| Mâts drapeaux | ❌ (3.5m) | ❌ | ✅ 3.5m | ❌ | Tubes longs, calage |
| LED perimeter | ❌ (poids/fragile) | ✅ (cases) | ❌ | ✅✅ | Flight cases, FCL requis |
| Brand scrubbing | ✅ | ✅ | ❌ | ❌ | Idéal |
| Cat 2 — Drapeaux | ✅ | ✅ | ❌ | ❌ | Très compact |
| Cat 2 — Decals | ✅ | ✅ | ❌ | ❌ | Idéal |
| Cat 2 — Press backdrops | ✅ | ✅ | ❌ | ⚠️ | Caisses |

### E.4 Synthèse packing — implications pour la modélisation

**Ce qui se charge bien (souple, gerbable, LCL OK) — ~90% du volume hors LED :**
Fence scrim, seat covers, vinyl, decals, brand scrubbing, vehicle wraps, drapeaux. Ces produits remplissent un conteneur de façon dense (taux de remplissage proche du 57% retenu). Compatibles LCL et FCL.

**Ce qui pose problème (le gabarit, pas le volume) :**
- **LED perimeter** : lourd (~210 kg/case), fragile, → **FCL obligatoire**, pas de LCL. C'est 39% du volume total.
- **Mâts drapeaux** : longueur 3.5m > limite LCL 3m → calage spécial ou flat-rack.
- **Building wraps** : rouleaux jusqu'à 3.2m → limite LCL en longueur.

**Règle de packing qui en découle (à intégrer au modèle) :**
> Le LED (39% du volume) impose du FCL et bloque le tout-LCL. Le reste (~61%) est majoritairement LCL-compatible. → Cohérent avec l'approche **hybride FCL+LCL** suggérée en limite du rapport MGT-530 : LED + mâts en FCL/flat-rack, souple en LCL.

### E.5 Taux de remplissage par profil (pour affiner le calcul FEU)

| Profil produit | Taux remplissage conteneur réaliste | Raison |
|---|---|---|
| Rouleaux souples gerbés | ~60% | Cylindres + vide inter-rouleaux |
| Cartons/ballots plats | ~70% | S'empilent bien |
| LED flight cases | ~75% | Conçus pour optimiser le 40ft |
| Mâts/tubes longs | ~35% | Beaucoup de vide autour |
| **Moyenne pondérée retenue** | **~57%** | (déjà appliquée dans les calculs m³) |

---

## PARTIE F — Nombre de palettes & dimensionnement de l'entrepôt

> Objectif : convertir les volumes en **nombre de palettes** par catégorie, pour dimensionner l'entrepôt intermédiaire (combien de positions palette y transitent / y sont stockées).

### F.0 La méthode (comment ça marche)

**Le piège à éviter** : on ne divise PAS le volume produit pur par le volume d'une palette. Une palette chargée contient du produit + du vide (entre rouleaux, etc.).

**La méthode cohérente** : on a déjà intégré le vide en calculant les **volumes conteneur** (×0.00056 ÷0.57). Une palette chargée occupe un volume "géométrique avec vides" — exactement la même nature que le volume conteneur. Donc :

```
Nombre de palettes = Volume conteneur (m³) ÷ Volume d'une palette chargée (m³)
```

**Volume d'une palette chargée** : base US GMA 1.22 × 1.02 m, hauteur de gerbage ~1.6 m
→ 1.22 × 1.02 × 1.6 = **~2.0 m³/palette** (valeur retenue pour les souples gerbés).

> Cas particuliers : le LED ne se palettise pas (flight cases → comptés en emplacements conteneur). Les mâts sont en fagots longs (hors palette standard).

### F.1 Palettes par produit — Catégorie 1 (planifiable)

| Produit | Volume conteneur (m³) | Vol./palette | Palettes | Profil |
|---|---|---|---|---|
| Fence scrim | 236 | 2.0 | **118** | Rouleaux gerbés |
| Building wraps | 160 | 2.0 | **80** | Rouleaux longs |
| Seat covers | 54 | 2.0 | **27** | Cartons |
| Pitch-side | 11 | 2.0 | **6** | Rouleaux |
| Wayfinding souple | 6 | 2.0 | **3** | Rouleaux |
| Vehicle wraps | 7 | 2.0 | **4** | Rouleaux |
| Intérieur (vinyl/fabric) | 912 | 2.0 | **456** | Rouleaux gerbés |
| Brand scrubbing | 68 | 2.0 | **34** | Rouleaux/ballots |
| Totems wayfinding (alu) | 140 | 1.7 | **82** | Caisses gerbées |
| **Sous-total palettes Cat 1** | | | **~810 palettes** | |
| Mâts drapeaux | 60 | (fagots) | **~100 fagots** | Tubes 3.5m, hors palette |
| LED perimeter | 1,072 | (flight cases) | **~16 emplacements conteneur** | 1 système/stade |

### F.2 Palettes par produit — Catégorie 2 (time-critical)

| Produit | Volume conteneur (m³) | Vol./palette | Palettes |
|---|---|---|---|
| Drapeaux nationaux | ~2 | 2.0 | **1** |
| Decals match | ~3.5 | 2.0 | **2** |
| Press backdrops | ~1 | 2.0 | **1** |
| **Sous-total palettes Cat 2** | ~6.5 | | **~4 palettes** |

### F.3 Synthèse — ce qui transite par l'entrepôt

| Flux | Palettes souples | Fagots | Emplacements LED | Total positions |
|---|---|---|---|---|
| **Cat 1 (planifiable)** | ~810 | ~100 | ~16 conteneurs | ~810 positions palette + spécial |
| **Cat 2 (time-critical)** | ~4 | — | — | ~4 positions palette |
| **TOTAL** | **~814 palettes** | ~100 fagots | ~16 LED | |

### F.4 Dimensionnement de l'entrepôt — comment l'utiliser

**Surface au sol nécessaire (stockage à plat, 1 niveau) :**
```
814 palettes × 1.24 m²/palette (1.22×1.02) = ~1,010 m² d'emprise palette pure
+ allées de circulation (×2 à ×2.5 typique) ≈ ~2,500 m² au sol
```

**Avec rayonnage gerbé (3 niveaux, standard entrepôt) :**
```
814 palettes ÷ 3 niveaux = ~270 positions au sol
≈ ~340 m² emprise + allées ≈ ~850-1,000 m² au sol
```

**Lecture clé pour ta modélisation :**

| Question entrepôt | Réponse |
|---|---|
| Combien de palettes au total ? | ~814 (dont 810 Cat 1, 4 Cat 2) |
| Combien stockées en permanence ? | Cat 2 : ~4 palettes "en attente" (volume minuscule) |
| Combien en transit (flux rapide) ? | Cat 1 : ~810 palettes qui passent et repartent vers les stades |
| Surface entrepôt mini (rayonnage 3 niveaux) | ~850-1,000 m² |
| Surface entrepôt (stockage à plat) | ~2,500 m² |

### F.5 L'insight pour ton modèle dynamique

**L'entrepôt a deux fonctions de tailles très différentes :**

1. **Hub de transit Cat 1 (gros débit, court séjour)** : ~810 palettes passent par l'entrepôt en début de tournoi, sont triées, et repartent vite vers les 16 stades. C'est un **flux**, pas un stock — l'entrepôt n'a pas besoin de les contenir toutes en même temps si le tri est rapide.

2. **Zone d'attente Cat 2 (petit volume, long séjour)** : seulement ~4 palettes restent en attente jusqu'aux résultats knockout, puis filent au site de production. C'est un **stock tampon minuscule** mais à séjour long.

> Conclusion modélisation : l'entrepôt est dimensionné par le **pic de débit Cat 1** (combien de palettes simultanément pendant la phase d'installation pré-tournoi), pas par le stock Cat 2 (négligeable). Si l'installation des 16 stades est étalée sur plusieurs semaines, le pic simultané est une fraction des 810 palettes.

> ⚠️ Hypothèses : palette US 2.0 m³, gerbage 3 niveaux, ratio allées ×2.5. Le LED (16 conteneurs) peut by-passer l'entrepôt (livraison directe port→stade) car il ne nécessite ni tri ni production — à décider selon ton modèle.

---

## PARTIE G — Poids par catégorie & saturation volume vs poids

> Objectif : ajouter le **poids** à l'inventaire pour vérifier si ce sont les m³ (volume) ou les tonnes (poids) qui saturent les conteneurs. Crucial pour le LED (lourd) et pour la cohérence avec le calcul CO2 du rapport.

### G.0 Poids surfaciques sources

| Matériau | Poids surfacique | Source |
|---|---|---|
| Fence scrim / mesh perforé | ~0.18 kg/m² | Camden Look spec (115g + structure) |
| Vinyl 13oz (building wrap, intérieur, decals) | ~0.67 kg/m² | Tampa Printing (4.03 m² = 2.72 kg) |
| Seat covers (tissu perforé) | ~0.30 kg/m² | Estimation tissu technique |
| Tissu drapeau polyester | ~0.13 kg/m² | Camden Look spec (110g flag) |
| Panneau LED perimeter | ~46 kg/panneau (1.44 m²) ≈ 32 kg/m² | TecMaschin (cabinet 46 kg) |

### G.1 Poids par produit — Catégorie 1

| Produit | m² | kg/m² | Poids total | Tonnes |
|---|---|---|---|---|
| Fence scrim | 240,000 | 0.18 | 43,200 kg | **43 t** |
| Building wraps | 163,000 | 0.67 | 109,210 kg | **109 t** |
| Seat covers | 55,000 | 0.30 | 16,500 kg | **17 t** |
| Pitch-side | 11,000 | 0.67 | 7,370 kg | **7 t** |
| Wayfinding souple | 5,600 | 0.30 | 1,680 kg | **2 t** |
| Vehicle wraps | 7,550 | 0.67 | 5,059 kg | **5 t** |
| Intérieur (vinyl/fabric) | 928,000 | 0.50 (mix) | 464,000 kg | **464 t** |
| Brand scrubbing | 69,000 | 0.50 | 34,500 kg | **35 t** |
| **Sous-total souple Cat 1** | | | | **~682 t** |
| LED perimeter | 33,300 m² équiv. | 32 | 1,065,600 kg | **~1,066 t** |
| Totems alu + mâts | — | — | ~80 t | **~80 t** |
| **TOTAL Cat 1** | | | | **~1,828 t** |

### G.2 Poids — Catégorie 2

| Produit | m² | kg/m² | Tonnes |
|---|---|---|---|
| Drapeaux | 1,800 | 0.13 | **0.2 t** |
| Decals | 3,600 | 0.67 | **2.4 t** |
| Press backdrops | 1,200 | 0.50 | **0.6 t** |
| **TOTAL Cat 2** | | | **~3 t** |

### G.3 Le test clé : volume vs poids — qu'est-ce qui sature le conteneur ?

Un FEU a **deux limites** : ~67 m³ de volume ET ~26 t de charge utile (payload max).

> **Règle** : un conteneur est "plein" dès qu'il atteint SA PREMIÈRE limite — soit le volume, soit le poids.

| Catégorie | Volume | Poids | Densité (kg/m³) | Limite atteinte en premier |
|---|---|---|---|---|
| Souple (rouleaux/vinyl) | 1,454 m³ | 682 t | ~470 kg/m³ | **VOLUME** (densité < 400 = volume sature) |
| LED perimeter | 1,072 m³ | 1,066 t | ~995 kg/m³ | ⚠️ **POIDS** (densité ~1,000 = poids sature) |
| Totems + mâts | 200 m³ | 80 t | ~400 kg/m³ | Limite (les deux à la fois) |

**Repère** : densité de "bascule" d'un FEU = 26 t ÷ 67 m³ ≈ **388 kg/m³**.
- Au-dessus → le **poids** sature (conteneur "lourd")
- En dessous → le **volume** sature (conteneur "léger")

### G.4 Ce que ça change CONCRÈTEMENT

**1. Le souple reste "volume-driven" (cohérent avec tout ce qu'on a fait)**
À ~470 kg/m³, le souple est juste au-dessus du seuil, mais en pratique les rouleaux ne se chargent pas à pleine densité → c'est bien le **volume** qui sature. Nos calculs FEU basés sur le volume sont **valides** pour le souple. ✅

**2. Le LED change de logique : il sature en POIDS, pas en volume** ⚠️
À ~1,000 kg/m³, un conteneur de LED atteint les 26 t **avant** d'être plein en volume. Conséquence directe :
- On avait dit "1 système LED = 1 conteneur 40ft" (basé sur le volume, JYVISIONS)
- Mais 67 m³ de LED pèserait ~67 t → **impossible** (max 26 t/FEU)
- **Donc un conteneur LED n'est rempli qu'à ~26 t ÷ 32 kg/m² ... = il part à moitié vide en volume mais plein en poids**

→ **Le LED a besoin de PLUS de conteneurs que le volume seul ne le suggère.** Si on recompte par le poids : 1,066 t ÷ 26 t/FEU = **~41 FEUs rien que pour le LED** (vs 16 estimés par le volume). C'est un écart majeur.

**3. Impact sur le total FEUs**

| Méthode | FEUs LED | FEUs souple | Total |
|---|---|---|---|
| Par le volume seul (notre calcul B.7) | ~16 | ~32 | **~61** |
| En tenant compte du poids LED | **~41** | ~32 | **~73-85** |

→ Le vrai nombre de FEUs est probablement **plus proche de 75-85 que de 61**, à cause de la contrainte poids du LED.

**4. Cohérence avec le CO2 du rapport**
Ton rapport utilise "10 t/FEU cargo léger". C'est vrai pour le souple (682 t ÷ 32 FEU ≈ 21 t/FEU... en fait plutôt mi-lourd). Mais pour le LED c'est ~26 t/FEU (plein poids). → Le poste CO2 maritime du LED est sous-estimé si on suppose 10 t/FEU.

### G.5 Synthèse poids

| | Volume | Poids | FEUs (volume) | FEUs (poids réel) |
|---|---|---|---|---|
| **Cat 1 souple** | 1,454 m³ | ~682 t | ~32 | ~32 (volume-driven) |
| **Cat 1 LED** | 1,072 m³ | ~1,066 t | ~16 | **~41 (poids-driven)** ⚠️ |
| **Cat 1 structures** | 200 m³ | ~80 t | ~4 | ~4 |
| **Cat 2** | 6.5 m³ | ~3 t | <1 | <1 |
| **TOTAL** | ~2,732 m³ | **~1,749 t** | ~61 | **~77** |

> 💡 **L'enseignement clé** : pour 90% de l'inventaire (le souple), le volume est la bonne métrique. Mais le **LED bascule en contrainte poids** et fait passer le total de ~61 à ~77 FEUs. Si tu exclus le LED (loué localement), tu retombes sur ~37 FEUs **volume-driven propre**, sans cette complication poids.

---

## Sources

### Sources Partie A (état des lieux)

| Donnée | Source |
|---|---|
| Format 2026 (16 stades, 104 matchs, 48 équipes, 39 jours) | Britannica ; StadiumDB ; Sky Sports |
| Étendue géo 4,000 miles, comparaison compacité Qatar | The Athletic / matchbingo |
| Capacités des 16 stades | FIFA ticketing FAQ ; StadiumDB ; Soccergraph ; Goal |
| Brand scrubbing — clause 6.4.ii contrat FIFA | The Mirror US ; The Athletic (Henry Bushnell) |
| Brand scrubbing — ~2,000 éléments Mercedes-Benz | Sports Business Journal / Facilities Dive (Drew Bryant, Elevate) |
| Charge plus légère sur stades récents (SoFi) | Facilities Dive |
| Debranding Lincoln Financial (4 logos façade, etc.) | Philadelphia Inquirer |
| Prestataires 2026 (The Look Company + Wasserman Live) | Coliseum (coliseum-online.com) |

### Sources Partie B (conversions — héritées de la reconstitution Qatar)

| Donnée | Source |
|---|---|
| Méthode ancrage volume (rouleau ARC 60"×150', 0.00056 m³/m²) | ARC Supplies / Aarongraphics |
| Ratio building wrap m²/stade | bluemedia Super Bowl LIII Atlanta |
| Seat covers ratio | CSM Live / Premier League (cityam.com) |
| LED perimeter = 1 conteneur 40ft/stade | JYVISIONS (jyvisions.com) |
| Quantités de référence Qatar 2022 | The Look Company case study |
| Dimensions FEU | Standard ISO |
