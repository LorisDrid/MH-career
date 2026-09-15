# AGENTS.md — MH-career

Manuel opératoire du projet. Ce fichier fait autorité : en cas de contradiction entre
une demande ponctuelle et les règles ci-dessous, les règles gagnent, et l'agent le
signale au lieu de contourner.

Références détaillées : [modèle de données](docs/DATA-MODEL.md) ·
[checklist de capture](docs/CAPTURE-CHECKLIST.md)

---

## 1. Le projet

Archiver et visualiser ~15 ans de statistiques personnelles Monster Hunter
(heures de jeu, monstres chassés, armes, rangs), réparties sur des jeux et des
plateformes qui n'exposent pas les mêmes compteurs.

**La valeur du projet est dans la donnée, pas dans le site.** Le site n'est qu'une
vue ; il doit rester remplaçable sans perte. Toute décision technique qui rendrait
la donnée dépendante de l'outil de rendu est à refuser.

Jeux couverts :

| ID | Jeu | Plateforme | Statut |
|---|---|---|---|
| `mh3u` | Monster Hunter 3 Ultimate | Nintendo 3DS | terminé, figé |
| `mh4u` | Monster Hunter 4 Ultimate | Nintendo 3DS | terminé, figé |
| `mhgen` | Monster Hunter Generations | Nintendo 3DS | terminé, figé |
| `mhw` | Monster Hunter: World | PlayStation 4 | terminé, figé |
| `mhrise` | Monster Hunter Rise (+ Sunbreak) | PC, Game Pass | terminé, figé |
| `mhwilds` | Monster Hunter Wilds | Steam | à venir, évolutif |

### Non-objectifs

- Ce n'est **pas un service** : pas de compte, pas d'inscription, pas de multi-utilisateur.
- Ce n'est **pas une base de données** : pas de serveur, pas de SQL, pas de backend.
- Ce n'est **pas un wiki Monster Hunter** : le référentiel de monstres ne contient
  que ce qui est nécessaire pour agréger *mes* stats, pas la totalité de la licence.
- Pas de contribution externe attendue : pas de `CONTRIBUTING.md`, pas de templates d'issue.

### Rythme d'évolution

Cinq jeux sur six sont figés définitivement. Le contenu bougera très peu après la
saisie initiale. **Optimiser pour la durabilité et la relecture, jamais pour la
vélocité d'itération** : une chaîne de build qui fonctionnera encore dans dix ans
sans rien réinstaller vaut mieux qu'un confort de développement supérieur.

---

## 2. Règles impératives

### 2.1 Git — interdit

L'agent **n'exécute aucune commande `git`**, sous aucune forme : ni `add`, ni
`commit`, ni `push`, ni `checkout`, ni `stash`, ni derrière `rtk`, ni dans un script.
Les commandes `git` en lecture seule (`status`, `log`, `diff`) ne sont pas non plus
à lancer spontanément.

L'utilisateur gère l'intégralité du versionnement. L'agent se contente de **proposer
un message de commit** en fin de tâche, au format conventionnel (voir §13).

Écrire ou modifier `.gitignore` reste autorisé : c'est un fichier, pas une commande git.

### 2.2 Dépendances — interdit

- **Aucun gestionnaire de paquets JavaScript**, jamais, ni directement, ni derrière
  `rtk`, PowerShell, cmd, bash, Docker, WSL ou un script intermédiaire. La liste
  exhaustive des outils concernés figure dans la politique de sécurité globale de
  l'utilisateur (`~/.claude/CLAUDE.md`), qui fait foi.
- **Aucun `pip install`.** Le code Python de ce projet utilise **exclusivement la
  bibliothèque standard**. C'est une contrainte de conception, pas une gêne : elle est
  ce qui garantit que le projet se rebuilde sur n'importe quelle machine avec un
  Python 3.12 nu.
- **Aucun téléchargement** de binaire, d'archive ou de bibliothèque (`curl`, `wget`,
  `Invoke-WebRequest`…) pour contourner ces règles.

Si une dépendance semble nécessaire, l'agent l'expose **dans sa réponse** — nom,
version, justification, alternative en stdlib — et laisse l'utilisateur décider.
Il ne l'installe pas et ne l'ajoute à aucun manifeste.

> Note pratique : un garde-fou intercepte les commandes shell contenant ces noms
> d'outils, **y compris quand ils n'apparaissent que dans du texte** (un heredoc qui
> les cite, par exemple). Pour écrire de la documentation qui les mentionne, utiliser
> l'outil d'écriture de fichier plutôt qu'une commande shell.

### 2.3 Intégrité des données — critique

> **Ne jamais inventer un chiffre.**

Une statistique n'entre dans le repo que si elle provient d'une source constatée :
une photo d'écran, une capture, une API. Cette règle prime sur toute demande de
« compléter », « estimer », « remplir les trous » ou « mettre des valeurs d'exemple ».

- Valeur inconnue ⇒ **champ absent** (TOML) ou **cellule vide** (CSV). **Jamais `0`.**
  `0` signifie « zéro constaté », ce qui est une information différente et vérifiable.
- Un chiffre plausible mais non vérifié est plus nuisible qu'une case vide : une fois
  commité, plus rien ne le distingue d'une donnée réelle.
- Si l'agent a besoin de données pour tester du code, elles vont dans `tests/fixtures/`
  avec des IDs manifestement fictifs (`test_monster_a`), **jamais dans `data/`**.

### 2.4 Données générées — ne pas éditer

Tout ce qui est sous `data/generated/` est produit par `tools/build.py`. Ne jamais
l'éditer à la main : la modification serait écrasée au build suivant, et pire, elle
créerait une divergence silencieuse entre la source et le rendu. Pour changer une
valeur affichée, on corrige la source ou l'agrégation.

### 2.5 Justifier tout choix technique — obligatoire

Toute proposition de techno, bibliothèque, format ou structure doit être accompagnée de :

1. **le critère retenu** — pourquoi ce critère domine ici ;
2. **l'alternative écartée** — et ce qu'on aurait choisi sous un critère différent.

Formulation attendue : *« X, parce que le critère qui prime ici est Y. Si on avait
priorisé Z, on aurait pris W, au prix de V. »*

Une recommandation sans alternative explicitée est une réponse incomplète.

### 2.6 Périmètre

Ce projet est une archive personnelle. Ne pas ajouter spontanément : analytics,
télémétrie, service worker, formulaire de contact, commentaires, newsletter, i18n
multi-langue, SEO avancé, ou toute mécanique conçue pour une audience. Si une idée
de ce type semble utile, la proposer dans la réponse, ne pas l'implémenter.

---

## 3. Stack et justifications

| Sujet | Choix | Critère décisif | Alternative écartée |
|---|---|---|---|
| Génération du site | **Zola 0.22.1** | Binaire Rust unique, aucun gestionnaire de paquets, déjà installé → l'agent peut builder et vérifier lui-même | **Astro** : meilleur confort de dev du marché (content collections typées, validation Zod, îlots interactifs), mais son écosystème est interdit ici, donc l'agent n'aurait jamais pu installer, builder ni tester. Sous un critère « qualité de l'outillage de dev », Astro gagnait. Sous le critère « autonomie de la chaîne », il perd. |
| Traitement des données | **Python 3.12, stdlib seule** | `tomllib`, `csv`, `json`, `dataclasses`, `unittest` couvrent 100% du besoin → zéro installation | **Python + Jinja2 + PyYAML** : chaîne à un seul outil, plus souple, mais 2 dépendances à installer et on perd le serveur de dev de Zola. **Rust** : cohérent avec Zola mais toolchain absente de la machine et surdimensionné pour ~2000 lignes de données. |
| Format des sources | **TOML** (métadonnées, référentiels) + **CSV** (tableaux volumineux) | `tomllib` et `csv` sont en stdlib ; TOML accepte les commentaires (traçabilité des sources) ; le CSV permet de saisir 200 compteurs dans un tableur puis de coller le fichier | **YAML** : plus compact pour l'imbriqué, mais dépendance externe et pièges connus (indentation, `no` converti en `false`). **JSON** : zéro dépendance mais pas de commentaires et saisie manuelle pénible — rédhibitoire pour un projet dont l'activité principale *est* la saisie manuelle. |
| Graphiques | **SVG généré en Python au build** | Zéro JS, zéro CDN, zéro requête tierce ; le site rendra à l'identique dans dix ans ; infobulles faisables en CSS pur | **ECharts via CDN** : heatmap/radar/sunburst prêts à l'emploi et rendu très soigné pour bien moins de code, mais dépendance tierce chargée dans le navigateur à chaque visite et site cassé si le CDN disparaît. Sous un critère « richesse visuelle à effort minimal », ECharts gagnait. |
| Hébergement | **Vercel** | Adresse indépendante du domaine personnel, dépôt inchangé, gratuit | **GitHub Pages** : une seule chaîne et un seul fournisseur, mais le domaine personnalisé du site utilisateur capture **tous** les chemins `<user>.github.io`, y compris les pages de projet — l'archive serait sortie sous le domaine du portfolio. Y échapper imposait de créer une organisation et de transférer le dépôt. **Cloudflare Pages** : équivalent à Vercel, écarté au choix de l'utilisateur. |
| Photos sources | Brutes **hors repo** + versions réduites commitées | Repo léger, mais chaque chiffre reste traçable à sa source — c'est l'intérêt même d'un projet d'archivage | **Tout hors repo** : plus de traçabilité visible. **Tout dans le repo** : plusieurs centaines de Mo dans l'historique, irréversible sans réécrire l'historique. |
| Langue | IDs/code/commits en **anglais**, prose en **français** | Les IDs sont des clés techniques stables : en anglais ils restent alignés sur les sources externes (wikis, API Steam) | Tout en français : confortable mais friction permanente au croisement avec les sources externes. |

### Versions de référence

- Zola **0.22.1** — `C:\WINDOWS\system32\zola.exe`
- Python **3.12.10** — `C:\Program Files\Python312\python.exe`

`tomllib` exige Python ≥ 3.11 : c'est le plancher du projet.

---

## 4. Chaîne de build

> **Python lit les sources, valide, agrège et écrit `data/generated/`.
> Zola ne lit que `data/generated/` et ne fait que du rendu.**

```
data/reference/*.toml  ┐
data/games/*/meta.toml ├─→  tools/build.py  ─→  data/generated/site.json
data/games/*/*.csv     ┘      (validation           data/generated/charts/*.svg
                               + agrégation                    │
                               + rendu SVG)                    ↓
                                                        zola build  ─→  public/
```

Ce contrat à un seul point de contact est délibéré : **toute la logique métier est en
Python, testable en isolation**, et Zola reste un détail d'implémentation remplaçable.
Si Zola devait disparaître, seuls les templates seraient à réécrire — pas une ligne
d'agrégation.

Corollaire : **aucun calcul dans les templates Tera.** Si une valeur manque à
l'affichage, on l'ajoute à `site.json`, on ne la recalcule pas côté rendu.

---

## 5. Commandes

```bash
python -m tools.build                        # valide, agrège, génère data/generated/
python -m tools.build --check                # validation seule, sortie non nulle si erreur
python -m unittest discover -s tests -t .    # tests unitaires (stdlib)
zola check                                   # liens et templates
zola build                                   # génère public/
zola serve                                   # serveur de dev avec live-reload
```

Le pipeline se lance **en module** (`-m`) et non en script : `python tools/build.py`
placerait `tools/` sur le `sys.path` au lieu de la racine, et les imports internes
échoueraient. Pour la même raison, `unittest` a besoin de `-t .` afin que le paquet
`tools` reste importable depuis le dossier de tests.

`zola build` exige que `data/generated/site.json` existe : lancer `python -m tools.build`
d'abord. Une donnée manquante fait échouer le build avec un code non nul plutôt que
de déployer un site vide — comportement vérifié, voir §10.

Aucune de ces commandes n'invoque de gestionnaire de paquets, et toutes sont
exécutables par l'agent. C'était le critère de sélection de la stack.

---

## 6. Arborescence

```
MH-career/
├── AGENTS.md                  ← ce fichier
├── README.md
├── config.toml                ← configuration Zola
├── .gitignore
├── data/
│   ├── reference/             ← référentiels canoniques, partagés entre jeux
│   │   ├── games.toml
│   │   ├── platforms.toml
│   │   ├── species.toml
│   │   ├── monsters.toml
│   │   └── weapons.toml
│   ├── games/                 ← données brutes, une entrée par jeu
│   │   └── <game_id>/
│   │       ├── meta.toml
│   │       ├── hunts.csv
│   │       └── weapons.csv
│   └── generated/             ← produit par build.py, jamais édité à la main
│       ├── site.json
│       ├── hunts-all.csv      ← toutes les chasses, format long, pour le tableur
│       ├── weapons-all.csv
│       └── charts/*.svg
├── tools/                     ← Python, stdlib uniquement
│   ├── __init__.py            ← indispensable à l'exécution en `-m`
│   ├── build.py               ← point d'entrée (CLI)
│   ├── model.py               ← dataclasses du domaine
│   ├── report.py              ← collecte des problèmes de validation
│   ├── loaders.py             ← lecture TOML/CSV, avec numéros de ligne
│   ├── validate.py            ← contrôles d'intégrité
│   ├── aggregate.py           ← calculs inter-jeux
│   ├── exports.py             ← exports plats CSV
│   └── charts.py              ← rendu SVG (phase 4, pas encore écrit)
├── tests/
│   ├── __init__.py
│   ├── test_loaders.py
│   ├── test_validate.py
│   ├── test_aggregate.py
│   └── fixtures/data/         ← univers fictif, jamais de vraies stats
├── content/                   ← markdown Zola (prose FR)
├── templates/                 ← Tera
├── static/                    ← css, images
├── docs/
│   ├── DATA-MODEL.md
│   └── CAPTURE-CHECKLIST.md
└── .github/workflows/deploy.yml
```

---

## 7. Modèle de données — résumé

Trois couches, strictement séparées. Détail complet dans [docs/DATA-MODEL.md](docs/DATA-MODEL.md).

1. **Référentiels canoniques** (`data/reference/`) — le vocabulaire partagé :
   monstres, armes (les 14 types plus le Chasseur Félyne de Generations), espèces, jeux, plateformes. Un ID stable par entité, valable
   pour toute la licence. C'est ce qui permet de croiser MH3U et Wilds.
2. **Données brutes par jeu** (`data/games/<id>/`) — uniquement ce que le jeu
   affiche réellement. Aucun schéma uniforme imposé : les jeux MH n'exposent pas
   les mêmes compteurs, et forcer un schéma commun obligerait à inventer.
3. **Agrégats** (`data/generated/`) — calculés, jamais écrits à la main.

### Conventions structurantes

- **IDs en `snake_case`, jamais de tiret.** Dans Tera, `monsters.rathalos-azure`
  serait interprété comme la soustraction `rathalos - azure`. Tous les IDs sont
  donc `rathalos_azure`, `great_sword`, `flying_wyvern`.
- **`absent` ≠ `0`.** Cellule CSV vide ou clé TOML absente = inconnu. `0` = zéro
  constaté. Le validateur ne doit jamais substituer l'un à l'autre, et le rendu
  doit les afficher différemment (« — » vs « 0 »).
- **Les variantes pointent vers leur forme de base** (`base = "rathalos"`), ce qui
  permet d'agréger « tous les Rathalos confondus » sans table de correspondance ad hoc.
- **Toute donnée a une source** : chaque `meta.toml` porte un bloc `[[sources]]`
  daté. Une valeur sans source est un bug de saisie.

---

## 8. Structure du site

| Route | Contenu |
|---|---|
| `/` | Totaux de carrière, timeline, faits saillants |
| `/games/` | Index des jeux |
| `/games/<id>/` | Stats détaillées + notes personnelles rédigées en markdown |
| `/bestiary/` | Bestiaire cumulé toutes licences, ventilé par jeu |
| `/weapons/` | Usage des armes et son évolution dans le temps |
| `/about/` | **Méthodologie** : d'où viennent les chiffres, ce qui manque et pourquoi |

La page `/about/` n'est pas optionnelle. Sur un projet d'archivage, documenter les
lacunes et la provenance fait partie du livrable : un chiffre dont on ignore l'origine
n'est pas exploitable.

Les vues croisées (`/bestiary/`, `/weapons/`) sont la raison d'être du projet. Un
classement par jeu, chaque jeu le fait déjà ; ce qu'aucun jeu ne peut dire, c'est
« premier Rathalos en 2013, dernier en 2026 ».

---

## 9. Conventions de code

### Python

- Stdlib uniquement. `dataclasses` pour les entités, `pathlib` pour les chemins,
  `typing` pour les annotations — tout est en stdlib, aucune excuse pour une dépendance.
- Annotations de type sur toute fonction publique.
- Aucune exception silencieuse : une donnée invalide **arrête le build** avec un
  message nommant le fichier et la ligne. Un build qui « passe quand même » en
  ignorant une erreur est la pire issue possible pour un projet d'archivage.
- Les messages d'erreur du validateur sont en français et actionnables :
  `data/games/mh4u/hunts.csv:42 — monster_id 'rathalos_azur' inconnu (voulais-tu 'rathalos_azure' ?)`.
- Tests en `unittest`, fixtures dans `tests/fixtures/`.

### Tera / HTML

- Aucun calcul dans les templates (voir §4). Boucles et conditions d'affichage seulement.
- Macros dans `templates/macros/` pour les éléments répétés (carte de stat, tableau).
- HTML sémantique. Les tableaux de données sont des `<table>` avec `<th scope>`.
- **Inconnu contre zéro : jamais `{% if %}` sur une valeur numérique.**

  Dans Tera, `null` **et** `0` sont falsy. `{% if hunted %}{{ hunted }}{% else %}—{% endif %}`
  afficherait donc « — » sur un zéro constaté, ce qui détruit silencieusement la
  distinction qui fonde tout le modèle de données. Utiliser exclusivement le filtre
  `default` :

  ```
  {{ hunted | default(value="—") }}
  ```

  Comportement vérifié sur Zola 0.22.1 : `null → —`, `0 → 0`, clé absente `→ —`.
  Python peut donc émettre indifféremment `null` ou omettre la clé ; les deux se
  rendent correctement.

### CSS

- Pas de framework. Propriétés personnalisées pour la palette, thème clair et sombre
  via `prefers-color-scheme`.
- Mobile d'abord. Les tableaux larges vont dans un conteneur `overflow-x: auto`.

---

## 10. Roadmap

### Phase 0 — Capture (utilisateur, sans code) · **priorité absolue**

Photographier toutes les Guild Cards et écrans de stats, **avant toute ligne de code**.

C'est la seule phase irréversible du projet. Une 3DS qui ne démarre plus, une pile de
sauvegarde vide, une save corrompue, et ces chiffres sont perdus définitivement. Le
code pourra toujours être réécrit ; pas eux.

Voir [docs/CAPTURE-CHECKLIST.md](docs/CAPTURE-CHECKLIST.md).

### Phase 1 — Pipeline vide et vert

Squelette du repo, référentiels de base, validateur, `build.py` produisant un
`site.json` **sans aucun jeu**, Zola qui l'affiche, CI qui déploie sur Pages.

Objectif : la chaîne complète tourne de bout en bout avant qu'il y ait la moindre
donnée réelle. Déboguer un pipeline et saisir des données sont deux activités
distinctes ; les mener en parallèle rend les deux plus difficiles.

#### Contrôle de faisabilité — ✅ validé sur Zola 0.22.1

Le contrat Python↔Zola de la §4 a été vérifié sur une maquette jetable avant tout
code de production :

| Vérification | Résultat |
|---|---|
| `load_data(path="…/site.json")`, accès imbriqué et boucles | fonctionne |
| `load_data(…, format="plain")` pour inliner un SVG | fonctionne, contenu verbatim |
| Fichier de données absent | **build en échec, code de sortie 1** |
| Distinction `null` / `0` via `\| default(value="—")` | correcte (voir §9) |

Le troisième point est celui qui compte pour la CI : une donnée manquante casse le
build au lieu de déployer un site vide. Aucun garde-fou supplémentaire n'est donc
nécessaire côté workflow.

### Phase 2 — Un jeu complet

`mh4u` en premier : c'est la Guild Card la plus riche du lot. Saisir un jeu
intégralement révèle d'un coup tous les défauts de modélisation, alors que saisir
cinq jeux à moitié les disperse.

### Phase 3 — Les autres jeux

`mh3u`, `mhgen`, `mhw`, `mhrise`. Le référentiel de monstres se complète au fil de
l'eau. Phase longue et ingrate : l'étaler est un choix assumé, pas un retard.

### Phase 4 — Vues croisées

Bestiaire cumulé, heatmap monstre × jeu, évolution des armes, timeline de carrière.
Graphiques SVG. C'est ici que le projet devient autre chose qu'un tableur.

### Phase 5 — Polish et synchro Steam

Soin visuel, puis synchronisation Steam pour `mhwilds`.

**Contrainte de conception de la synchro** : 3DS, PS4 et Xbox Game Pass n'exposent
aucune API gratuite exploitable. La saisie manuelle reste donc le chemin principal,
et Steam n'est qu'une couche additive. Concrètement, la synchro écrit dans un fichier
séparé (`data/games/mhwilds/steam.toml`) fusionné au build, et **n'écrase jamais une
valeur saisie à la main**. Limite à connaître : Steam donne le temps de jeu et les
succès, jamais le détail « 247 Rathalos » — celui-ci reste dans la sauvegarde locale.

---

## 11. Déploiement

**Vercel construit et publie le site à chaque push.** Tout tient dans deux
fichiers : `vercel.json` (commande de build, dossier de sortie) et
`tools/deploy.py` (le build lui-même).

`tools/deploy.py` télécharge Zola à **version épinglée**, vérifie son empreinte
SHA-256, génère les données puis construit le site. Il est écrit en Python
stdlib plutôt qu'en commande shell dans la configuration Vercel : la discipline
de version épinglée était le point le plus fragile de la chaîne, et elle est
plus lisible et plus modifiable dans du code que dans une chaîne de
configuration.

Tant que `ZOLA_SHA256` est vide, le téléchargement n'est pas vérifié et un
avertissement le signale dans le journal de build — l'absence de contrôle reste
visible au lieu d'être silencieuse. La valeur se relève dans le journal du
premier déploiement.

**`base_url` n'est pas figé dans `config.toml` pour la production.**
`tools/deploy.py` lit `VERCEL_PROJECT_PRODUCTION_URL` dans l'environnement et le
passe à `zola build --base-url`. Le site ne dépend donc pas du nom que Vercel
attribue au projet. La valeur du fichier de configuration ne sert qu'aux
constructions locales.

Vercel sert le site à la **racine** de son domaine : il n'y a pas de
sous-chemin, et le piège classique du déploiement en sous-répertoire ne
s'applique pas ici.

> Pourquoi pas GitHub Pages : le site utilisateur du compte porte un domaine
> personnalisé, et GitHub redirige alors **tous** les chemins de
> `<user>.github.io` vers ce domaine, y compris les pages de projet. L'archive
> se serait retrouvée servie sous le domaine du portfolio, ce qui n'était pas
> souhaité. Sous un critère « une seule chaîne, un seul fournisseur », GitHub
> Pages restait préférable ; sous le critère « adresse indépendante », il ne
> pouvait pas répondre sans créer une organisation.

### Ce que la CI fait, et ne fait pas

`.github/workflows/ci.yml` ne déploie rien. Il lance les tests et la validation
des données, pour qu'une erreur apparaisse sur le dépôt et pas seulement dans le
journal d'un autre service. Il n'installe pas Zola : la construction du site est
vérifiée par le déploiement Vercel, qui échoue et ne publie rien si un template
casse.

## 12. Définition du « terminé »

Une tâche n'est terminée que si :

- [ ] `python -m tools.build --check` sort en 0
- [ ] `python -m unittest discover -s tests -t .` est vert
- [ ] `zola build` passe sans warning
- [ ] toute donnée ajoutée référence une source dans `[[sources]]`
- [ ] aucune valeur inventée, aucun `0` substitué à un inconnu
- [ ] les choix techniques introduits sont justifiés (critère + alternative écartée)

---

## 13. Messages de commit

L'agent **propose** ces messages ; l'utilisateur commite. Format conventionnel :

| Type | Usage |
|---|---|
| `feat:` | nouvelle fonctionnalité du site ou du pipeline |
| `fix:` | correction de bug |
| `data:` | saisie ou correction de statistiques — scope obligatoire |
| `refactor:` | restructuration sans changement de comportement |
| `docs:` | documentation |
| `style:` | mise en forme, CSS |
| `test:` | tests |
| `ci:` | workflows GitHub Actions |
| `chore:` | maintenance diverse |

Scope entre parenthèses quand c'est pertinent, en particulier pour `data:` :

```
data(mh4u): add guild card stats and hunt tallies
feat(bestiary): add cross-game monster aggregation
fix(validate): reject captured greater than hunted
docs: add AGENTS.md, data model and capture checklist
```

Messages en anglais, impératif présent, pas de point final.

### Découpage en plusieurs commits

Dès que l'agent propose **plus d'un commit**, il donne pour chacun la commande
`git add` correspondante, dans l'ordre d'application. Un seul commit proposé
implique `git add .`, inutile de le préciser.

Sans cela, l'utilisateur devrait reconstituer lui-même quel fichier va dans quel
commit, ce qui annule le bénéfice du découpage.

Avant de proposer, vérifier que l'union des `git add` couvre tous les fichiers
modifiés, qu'aucun n'apparaît dans deux commits, et que l'ordre est cohérent —
par exemple `.gitignore` avant les fichiers qu'il protège.
