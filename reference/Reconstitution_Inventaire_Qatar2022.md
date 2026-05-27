# Reconstitution de l'inventaire de branding — The Look Company, Qatar 2022
## Méthodologie ancrée : m² → m³ → FEUs

> Projet MGT-530 (FIFA World Cup 2026 — Venue Signage Distribution)
> Objectif : reconstituer la répartition des **905,000 m²** de branding produits par The Look Company pour Qatar 2022, puis convertir en volume (m³) et conteneurs (FEUs).
> Hypothèses de modélisation : **tout vient de Chine** (y compris LED) ; périmètre = **stades + précinct immédiat**.

---

## 0. Cadre et hypothèses de modélisation

**Cible totale** : 905,000 m² de matériaux brandés (source : The Look Company, case study Qatar 2022).

**Périmètre retenu** : stades + précinct immédiat (clôtures, entrées, wayfinding du précinct). On **exclut** le city dressing pur (street banners sur lampadaires de Doha) et les 108 venues non-compétition — gérés séparément.

**Choix "tout vient de Chine"** : on inclut le LED perimeter dans le flux maritime, même si en réalité il est souvent loué. Justification : la Chine fabrique l'essentiel des écrans perimeter mondiaux, et ce choix donne une borne haute défendable pour le dimensionnement logistique.

**Les 3 niveaux de confiance :**
- 🟢 Niveau 1 — Calculable depuis les quantités publiées par The Look Company
- 🟡 Niveau 2 — Adapté de ratios d'autres sources (bluemedia, Euro 2024, fournisseurs)
- 🔴 Niveau 3 — Hypothèse de répartition pour combler les trous

---

## 1. Périmètre : combien des 905,000 m² gardons-nous ?

| Composant | m² estimés | Dans le scope (stade+précinct) ? |
|---|---|---|
| Street banners (lampadaires ville) | ~70,000 | ❌ City dressing — exclu |
| Flags ville | ~6,000 | ❌ Exclu (part ville) |
| 108 venues non-compétition | ~189,000 | ❌ Exclu (hors stade) |
| Vehicle wraps (bus/véhicules officiels) | ~7,550 | ✅ Gardé (transport officiel, rattaché au dispositif) |
| **Tout le reste (stades + précinct)** | **~640,000** | ✅ **Gardé (~71%)** |

> La part "perdue" (city + venues) est estimée à **~29%** (fourchette 25-35% selon la taille supposée des 108 venues, donnée inconnue).
> Les **151 véhicules** (~7,550 m²) sont inclus dans le scope : ce sont les bus/véhicules officiels du dispositif, fabriqués et livrés au même titre que le reste.

**m² retenus pour la reconstitution : ~640,000 m²** (dont ~7,550 m² de vehicle wraps ; soit ~80,000 m²/stade pour 8 stades).

---

## 2. ÉTAPE 1 — Répartition des m² par produit (sur les 640,000 m² retenus)

### 🟢 Niveau 1 — Calculable (The Look Company)

| Produit | Quantité | Dimension unitaire | m² | Source dimension |
|---|---|---|---|---|
| Fence scrim (part stade/précinct) | ~60 km (sur 87 km total, le reste en ville) | hauteur ~2 m | **120,000 m²** | Camden Look spec (scrim 0.9-1.2m, posé multi-rangées) |
| Wayfinding structures (précinct) | ~700 (sur 1,000) | ~4 m²/structure | **2,800 m²** | Hypothèse totem 2 faces |
| Vehicle wraps (bus/véhicules officiels) | 151 véhicules | ~50 m²/véhicule (bus ~12m × 2 côtés + arrière) | **7,550 m²** | Calcul géométrique bus standard |

**Sous-total Niveau 1 : ~130,000 m²**

### 🟡 Niveau 2 — Adapté d'autres sources

| Produit | Base | Ratio | m² | Source ratio |
|---|---|---|---|---|
| Building wraps (façades) | 8 stades | ~9,300 m²/stade | **74,400 m²** | bluemedia SB LIII Atlanta (>100,000 sq ft façade) |
| Perimeter / pitch-side imprimé | 8 stades | ~700 m²/stade | **5,600 m²** | Calcul géométrique terrain FIFA 105×68m, périmètre ~340m |
| Seat covers / section covers | 8 stades | ~3,000 m²/stade | **24,000 m²** | Adapté CSM Live / Premier League (cityam.com) |

**Sous-total Niveau 2 : ~104,000 m²**

### 🔴 Niveau 3 — Hypothèse (résidu = intérieur des stades)

```
Cible scope :          640,000 m²
− Niveau 1 :          −130,000 m²
− Niveau 2 :          −104,000 m²
──────────────────────────────────
= Résidu intérieur :   406,000 m²
```

Réparti sur 8 stades → **~50,750 m²/stade** de branding intérieur (concourses, tunnels, vestiaires, suites VIP, centres médias, vomitoires, decals, wayfinding intérieur). Cohérent pour un grand stade entièrement habillé.

### Récapitulatif ÉTAPE 1

| Niveau | Catégorie | m² | % |
|---|---|---|---|
| 🟢 1 | Fence scrim + wayfinding précinct + véhicules | 130,000 | 20% |
| 🟡 2 | Building wraps, pitch-side, seat covers | 104,000 | 16% |
| 🔴 3 | Intérieur stades (résidu) | 406,000 | 64% |
| | **TOTAL scope** | **~640,000 m²** | 100% |

---

## 3. ÉTAPE 2 — Conversion m² → m³ (méthode ancrée)

### Donnée d'ancrage (rouleau réel mesurable)

Rouleau standard PVC mesh/scrim (réf. ARC 14mil, 60" × 150') :
- Surface : 1.52 m × 45.7 m = **69.5 m²**
- Volume enroulé (cylindre Ø~0.18m, long. 1.55m) : π × 0.09² × 1.55 ≈ **0.039 m³**
- → **1 m² enroulé serré ≈ 0.00056 m³** (matériau pur, sans vide entre rouleaux)

Source : dimensions rouleau ARC Supplies / Aarongraphics + spec poids Camden (scrim 115g/m², vinyl 13oz ≈ 0.67 kg/m² mesuré sur bannière Tampa Printing 4.03 m² = 2.72 kg).

### Du rouleau pur au volume conteneur

En conteneur réel, on perd ~40-45% en vide (rouleaux cylindriques non imbriqués, palettes, caisses).
**Taux de remplissage conteneur retenu : 57%.**

`V conteneur = (m² × 0.00056) ÷ 0.57`

### Calcul matériaux souples

| Catégorie | m² | Volume pur (m³) | Volume conteneur (m³) |
|---|---|---|---|
| Fence scrim | 120,000 | 67 | 118 |
| Building wraps | 74,400 | 42 | 73 |
| Seat covers | 24,000 | 13 | 24 |
| Pitch-side imprimé | 5,600 | 3 | 5 |
| Vehicle wraps | 7,550 | 4 | 7 |
| Intérieur (vinyl/fabric) | 406,000 | 227 | 399 |
| **Sous-total souple** | 637,550 | ~356 | **~626 m³** |

### Calcul structures rigides + LED (volume séparé, ancré)

| Structure | Quantité | Volume packé unitaire | Volume total | Source ancrage |
|---|---|---|---|---|
| LED perimeter boards | 8 stades × ~190 panneaux | système complet ≈ 1 conteneur 40ft/stade | **~67 m³/stade × 8 = 536 m³** | JYVISIONS (système complet = 1× 40ft container) |
| Wayfinding totems (alu) | 700 unités | ~0.1 m³/unité démontée | **70 m³** | Estimation cadre alu démonté |
| Mâts drapeaux / structures | inclus précinct | — | **~30 m³** | Estimation tubes |
| **Sous-total rigide + LED** | | | **~636 m³** | |

> ⚠️ Le LED domine le poste rigide (536 m³). Si on l'excluait (loué localement), le rigide tomberait à ~100 m³ et le total à ~725 m³. Le choix "tout de Chine" gonfle donc le total d'environ +430 m³.

### Récapitulatif ÉTAPE 2

| Type | Volume |
|---|---|
| Matériaux souples (rouleaux) | ~626 m³ |
| Structures rigides + LED | ~636 m³ |
| **VOLUME TOTAL (scope stade+précinct, tout de Chine)** | **~1,262 m³** |

---

## 4. ÉTAPE 3 — Conversion m³ → FEUs

### Données conteneur

| Paramètre | Valeur | Source |
|---|---|---|
| Volume brut FEU 40ft | ~67 m³ | Standard ISO |
| Remplissage utile réaliste | 45 m³/FEU | Médian entre 33 (conservateur) et 67 (théorique) |

### Calcul

```
Volume total : 1,262 m³
÷ 45 m³/FEU
─────────────────
= ~28 FEUs
```

### Fourchette selon remplissage

| Hypothèse remplissage | FEUs |
|---|---|
| Conservateur (33 m³/FEU) | ~38 FEUs |
| Réaliste (45 m³/FEU) | ~28 FEUs |
| Optimiste (60 m³/FEU) | ~21 FEUs |

---

## 5. SYNTHÈSE

### Résultat Qatar 2022 (scope stade+précinct, tout de Chine)

| Métrique | Valeur |
|---|---|
| m² de branding (scope) | ~640,000 m² (sur 905,000 m² totaux) |
| Volume total | **~1,262 m³** |
| Nombre de FEUs | **~28** (fourchette 21-38) |
| Par stade (÷8) | ~158 m³/stade, ~3.5 FEUs/stade |

### Décomposition du volume

| Poste | Volume | % | Confiance |
|---|---|---|---|
| Intérieur stades (souple) | 399 m³ | 32% | 🔴 hypothèse |
| LED perimeter | 536 m³ | 42% | 🟡 ancré (système=1 conteneur) |
| Fence scrim | 118 m³ | 9% | 🟢 calculable |
| Building wraps | 73 m³ | 6% | 🟡 ratio bluemedia |
| Autres (seat covers, totems, pitch-side, mâts, véhicules) | 136 m³ | 11% | mixte |

### Les 3 incertitudes majeures (pour analyse de sensibilité)

1. **Le LED (42% du volume)** : selon qu'on l'inclut ou non, le total passe de ~725 m³ à ~1,262 m³. C'est le plus gros levier.
2. **L'intérieur des stades (32%)** : pur résidu/hypothèse (Niveau 3), aucune donnée directe.
3. **Hauteur du fence scrim** : à 0.9m au lieu de 2m, le poste fence est divisé par ~2.

---

## 6. Sources

| Donnée | Source |
|---|---|
| Quantités Qatar 2022 (87km scrim, 21693 banners, 3300 flags, 1000 wayfinding, 151 véhicules, 905,000 m²) | The Look Company case study (thelookcompany.com) |
| Poids/dimensions scrim, banner flag (spec officielle event assets) | Camden Council "Look" spec sheet (camdocs.camden.gov.uk) |
| Dimension rouleau mesh 60"×150' (ancrage volume) | ARC Supplies / Aarongraphics |
| Poids vinyl 13oz réel (bannière 4.03 m² = 2.72 kg) | Tampa Printing / Walmart listing |
| Building wrap m²/stade | bluemedia Super Bowl LIII Atlanta (bluemedia.com / Yahoo Sports) |
| Seat covers ratio | CSM Live / Premier League (cityam.com) |
| LED perimeter : système complet = 1 conteneur 40ft, panneaux 1600×900×98mm | JYVISIONS (jyvisions.com) ; TecMaschin transport box specs |
| LED fabriqué en Chine pour stades mondiaux | Leeman LED FIFA (leemanled.com) |
| Fan zone inventory (référence city) | Tender Host City Cologne Euro 2024 (business.gov.uk) |
| Dimensions FEU | Standard ISO |
