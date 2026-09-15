# Modèle de données

Référence détaillée du schéma. Le résumé et les règles impératives sont dans
[AGENTS.md](../AGENTS.md).

---

## Principes

**Trois couches, strictement séparées.**

| Couche | Emplacement | Écrit par | Nature |
|---|---|---|---|
| 1. Référentiels canoniques | `data/reference/` | humain | vocabulaire partagé entre tous les jeux |
| 2. Données brutes par jeu | `data/games/<id>/` | humain (ou synchro Steam) | ce que le jeu affiche, rien de plus |
| 3. Agrégats | `data/generated/` | `tools/build.py` | calculé, jamais édité |

La séparation 1/2 est ce qui rend le projet intéressant : sans référentiel commun,
« Rathalos » dans MH3U et « Rathalos » dans Wilds seraient deux chaînes sans lien, et
aucune vue croisée ne serait possible.

**On ne stocke que ce que le jeu affiche réellement.** Les titres Monster Hunter
n'exposent pas les mêmes compteurs : imposer un schéma uniforme obligerait à combler
les trous, donc à inventer. Un champ non affiché par le jeu est simplement absent.

---

## Conventions transversales

### Identifiants

- `snake_case` **strictement**, jamais de tiret, jamais d'espace, jamais d'accent.
  Raison technique : dans Tera, `monsters.rathalos-azure` est évalué comme la
  soustraction `rathalos - azure`.
- Dérivés du nom **anglais**, qui est la forme stable à travers les jeux et les
  sources externes : `rathalos`, `rathalos_azure`, `great_sword`, `flying_wyvern`.
- Un ID, une fois commité, **ne change plus**. Le renommer casserait tous les CSV qui
  le référencent. En cas d'erreur, corriger partout en une seule fois.

### Inconnu contre zéro

C'est la convention la plus importante du projet.

| Écriture | Signification |
|---|---|
| clé TOML absente | la donnée n'existe pas ou n'a pas été relevée |
| cellule CSV vide | idem |
| `0` | zéro **constaté** : le jeu affiche bien 0 |

Le validateur ne substitue jamais l'un à l'autre, et le rendu les distingue
visuellement : « — » pour inconnu, « 0 » pour zéro constaté.

### Dates

- Période de jeu : `"YYYY-MM"` (chaîne, pas date TOML — les dates TOML natives
  exigent un jour, qu'on ne connaît pas).
- Date de capture d'une source : `"YYYY-MM-DD"`.

### Temps de jeu

Stocké en **minutes entières**, dans `playtime_minutes`, accompagné de
`playtime_precision` :

| `playtime_precision` | Signification |
|---|---|
| `"minutes"` | le jeu affichait `HH:MM`, transcription exacte |
| `"hours"` | le jeu n'affichait que des heures entières, valeur arrondie |

Enregistrer la précision plutôt que de la perdre silencieusement : sans ce champ,
un total de carrière laisserait croire à une exactitude à la minute qui n'existe pas.

---

## Couche 1 — Référentiels (`data/reference/`)

### `platforms.toml`

```toml
[platforms.nintendo_3ds]
name = "Nintendo 3DS"
manufacturer = "Nintendo"
released = 2011
```

### `games.toml`

```toml
[games.mh4u]
title = "Monster Hunter 4 Ultimate"
short_title = "MH4U"
platform = "nintendo_3ds"
generation = 4
released = 2015          # sortie occidentale
played_from = "2015-02"  # quand MOI j'y ai joué
played_to = "2016-01"
status = "finished"      # finished | ongoing | planned
```

`played_from` / `played_to` alimentent la timeline de carrière et datent les vues
croisées. Aucun jeu MH n'enregistre la date d'une chasse individuelle : « premier
Rathalos en 2013 » se déduit de la période de jeu, pas d'un horodatage. Cette
approximation doit être assumée et expliquée sur `/about/`.

### `species.toml`

```toml
[species.flying_wyvern]
name_en = "Flying Wyvern"
name_fr = "Wyverne volante"
```

### `monsters.toml`

```toml
[monsters.rathalos]
name_en = "Rathalos"
name_fr = "Rathalos"
species = "flying_wyvern"
debut = "mh1"

[monsters.rathalos_azure]
name_en = "Azure Rathalos"
name_fr = "Rathalos azur"
species = "flying_wyvern"
debut = "mh1"
base = "rathalos"           # forme de base
variant_type = "subspecies" # subspecies | rare_species | deviant | apex | variant
```

| Champ | Requis | Description |
|---|---|---|
| `name_en` | oui | nom anglais, source des IDs |
| `name_fr` | oui | nom français, affiché sur le site |
| `species` | **non** | clé de `species.toml` — voir ci-dessous |
| `debut` | non | ID du jeu de première apparition |
| `base` | non | présent **uniquement** sur une variante |
| `variant_type` | non | obligatoire si `base` est présent |

`species` est **optionnelle à dessein** : aucune Guild Card n'affiche l'espèce
d'un monstre. L'exiger obligerait à la tirer d'une source externe au jeu, ce que
le principe « on ne stocke que ce que le jeu affiche » proscrit. On la renseigne
quand on l'a vérifiée, jamais par défaut.

La relation `base` est le pivot du bestiaire cumulé : elle permet de totaliser
« tous les Rathalos confondus » sans table de correspondance ad hoc, tout en
conservant le détail par forme.

Le référentiel se remplit **au fil de la saisie**, pas d'avance. Y mettre les 200+
monstres de la licence avant d'en avoir besoin serait du travail de wiki, hors sujet
(cf. non-objectifs).

### `weapons.toml`

Les 14 types d'armes.

```toml
[weapons.great_sword]
name_en = "Great Sword"
name_fr = "Grande épée"
category = "melee"        # melee | ranged
introduced = "mh1"
```

IDs : `great_sword`, `long_sword`, `sword_and_shield`, `dual_blades`, `hammer`,
`hunting_horn`, `lance`, `gunlance`, `switch_axe`, `charge_blade`, `insect_glaive`,
`light_bowgun`, `heavy_bowgun`, `bow`.

Le champ `introduced` permet de ne pas afficher une arme sur un jeu antérieur à son
apparition — une case vide et une arme inexistante ne se rendent pas pareil. Les
valeurs exactes sont à vérifier à la saisie plutôt qu'à supposer.

---

## Couche 2 — Données par jeu (`data/games/<game_id>/`)

### `meta.toml`

```toml
game = "mh4u"

[progress]
hunter_name = "loris kill"
title = "Aventurier en Volto-hache"
hunter_rank = 4
playtime_minutes = 5322
playtime_precision = "minutes"
primary_weapon = "long_sword"

# Ventilation telle que la Guild Card l'affiche, et non un total unique : les
# jeux découpent leurs quêtes différemment. Les clés sont propres à chaque jeu.
# Le total n'est jamais saisi, il est calculé à l'agrégation.
[progress.quests]
caravan_low = 67
caravan_high = 14
guild_hall_low = 59
guild_hall_high = 0
g_rank = 0
guild_quests = 0
arena = 8

[[sources]]
kind = "guild_card"       # guild_card | hunter_notes | hunting_log | platform_stats | api
captured_on = "2026-09-20"
image = "static/sources/mh4u/guild-card-p1.jpg"
note = "page 1 : rang, temps de jeu, quêtes"

[[sources]]
kind = "hunter_notes"
captured_on = "2026-09-20"
image = "static/sources/mh4u/hunter-notes-01.jpg"
```

Tous les champs de `[progress]` sont **optionnels**. On n'écrit que ce que la console
affichait. Omettre est la bonne réponse ; mettre `0` est une erreur de saisie.

Le bloc `[[sources]]` est obligatoire dès qu'il y a au moins une valeur : c'est ce qui
rend un chiffre vérifiable dans cinq ans.

### `hunts.csv`

```csv
monster_id,hunted,captured,notes
rathalos,247,12,
rathalos_azure,88,,pas de compteur de capture sur cet écran
gore_magala,0,0,croisé mais jamais chassé
```

| Colonne | Type | Description |
|---|---|---|
| `monster_id` | clé de `monsters.toml` | doit exister, sinon le build échoue |
| `hunted` | entier >= 0, ou vide | nombre de chasses |
| `captured` | entier >= 0, ou vide | nombre de captures, si le jeu le distingue |
| `notes` | texte libre | contexte de saisie, en français |

Ligne 2 de l'exemple : `captured` vide = le jeu ne l'affichait pas.
Ligne 3 : `0` explicite = compteur bien présent, à zéro.

Le CSV est choisi ici précisément parce que ce tableau fait 100 à 200 lignes par jeu :
il se remplit dans un tableur en lisant les photos, puis se colle tel quel.

### `weapons.csv`

```csv
weapon_id,uses,notes
long_sword,412,
great_sword,88,
insect_glaive,,arme absente du compteur de ce jeu
```

`uses` est le compteur affiché par le jeu (souvent un nombre de quêtes menées avec
cette arme). Sa définition variant d'un titre à l'autre, ne jamais additionner `uses`
entre jeux sans le signaler : l'agrégation produit un **classement**, pas un total.

### `steam.toml` — phase 5, `mhwilds` uniquement

Écrit par la synchro automatique, jamais à la main. Fusionné au build en
**complément** de `meta.toml`, jamais en écrasement : une valeur saisie
manuellement l'emporte toujours sur une valeur d'API.

---

## Couche 3 — Généré (`data/generated/`)

### `site.json`

Structure indicative, à figer en phase 1.

```json
{
  "meta": { "schema_version": 1, "built_at": "2026-09-20T18:00:00Z" },
  "totals": {
    "games": 6,
    "playtime_minutes": 0,
    "playtime_precision": "hours",
    "hunts": 0,
    "distinct_monsters": 0,
    "career_span_years": 0
  },
  "games": [ { "id": "mh4u", "title": "...", "progress": {}, "top_monsters": [] } ],
  "bestiary": [
    {
      "id": "rathalos",
      "name_fr": "Rathalos",
      "total_hunted": 0,
      "forms": [],
      "per_game": { "mh4u": 247 },
      "first_game": "mh3u",
      "last_game": "mhrise"
    }
  ],
  "weapons": [],
  "timeline": []
}
```

Règles :
- `totals.playtime_precision` vaut `"hours"` dès qu'**un seul** jeu est en précision
  horaire : un total ne peut pas être plus précis que son terme le plus grossier.
- Un agrégat dont tous les termes sont inconnus reste `null`, pas `0`.
- `schema_version` est incrémenté à chaque changement cassant de structure, pour que
  les templates puissent échouer explicitement plutôt que d'afficher du vide.

### Exports plats

`hunts-all.csv` et `weapons-all.csv` reprennent toutes les observations au
**format long** : une ligne par couple (jeu, monstre), le jeu en colonne. Ils
existent pour être ouverts au tableur.

Les sources, elles, restent **découpées par jeu**. La forme de saisie et la forme
d'analyse sont deux choses différentes : garder un fichier par jeu rend
structurellement impossible qu'une erreur de saisie sur un jeu en corrompe un
autre — ce que le validateur ne pourrait pas rattraper, un mauvais chiffre restant
un chiffre valide. L'export rend la vue croisée sans payer ce risque.

`base_form` y est résolue, ce qui permet de regrouper les variantes dans un
tableur sans connaître le référentiel. Une valeur inconnue reste une **cellule
vide**, jamais un zéro.

### `charts/*.svg`

SVG rendus au build, inlinés dans les templates via
`load_data(path="...", format="plain")` plutôt qu'en `<img>` : inlinés, ils restent
stylables en CSS (thème clair/sombre) et peuvent réagir au survol sans JavaScript.

---

## Contrôles de validation

À implémenter dans `tools/validate.py` (phase 1). Toute violation **arrête le build**.

**Intégrité référentielle**
- tout `monster_id` d'un `hunts.csv` existe dans `monsters.toml`
- tout `weapon_id` d'un `weapons.csv` existe dans `weapons.toml`
- tout `base` de `monsters.toml` pointe vers un monstre existant, qui n'est pas
  lui-même une variante (pas de chaîne de variantes)
- `species`, `platform`, `debut`, `introduced` pointent vers des entrées existantes
- tout dossier de `data/games/` correspond à une entrée de `games.toml`, et inversement

**Unicité et forme**
- IDs uniques dans chaque référentiel
- IDs conformes à `^[a-z][a-z0-9_]*$` — c'est ce contrôle qui interdit les tirets
- pas de `monster_id` en doublon dans un même `hunts.csv`

**Cohérence des valeurs**
- compteurs entiers `>= 0`
- `captured <= hunted` quand les deux sont renseignés
- `variant_type` présent si et seulement si `base` l'est
- `playtime_precision` présent si `playtime_minutes` l'est
- clés de `[progress.quests]` en snake_case, valeurs entières `>= 0`
- `played_from <= played_to`, format `YYYY-MM`
- `captured_on` au format `YYYY-MM-DD`, pas dans le futur

**Traçabilité**
- tout `meta.toml` ayant au moins une valeur de `[progress]` a au moins un `[[sources]]`
- tout `image` de `[[sources]]` pointe vers un fichier existant

**Avertissements** (n'arrêtent pas le build, mais s'affichent)
- monstre présent dans `monsters.toml` mais référencé par aucun jeu
- jeu sans aucune donnée de chasse
