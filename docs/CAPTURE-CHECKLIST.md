# Checklist de capture — Phase 0

Phase 0 de la roadmap définie dans [AGENTS.md](../AGENTS.md). Le schéma dans lequel
ces relevés seront saisis est décrit dans [DATA-MODEL.md](DATA-MODEL.md).

Ce document est **fait pour être amendé pendant la capture**, pas pour être exact du
premier coup. Les chemins de menu sont indicatifs : les corriger ici au fur et à
mesure, console en main.

---

## Pourquoi cette phase d'abord

C'est la seule étape irréversible du projet.

Les cartouches 3DS n'ont pas de pile de sauvegarde, donc le risque de perte spontanée
est plus faible qu'on ne le croit souvent. Mais une console qui ne démarre plus, un
lecteur de cartouche défaillant, une cartouche égarée, un compte PSN ou Xbox fermé
produisent le même résultat : ces chiffres n'existent nulle part ailleurs.

Le code pourra toujours être réécrit. Ces écrans, non. **Capturer avant de coder.**

Corollaire pratique : il n'est pas nécessaire de savoir quoi faire de la donnée pour
la capturer. Photographier large et trier plus tard est la bonne stratégie — repasser
une seconde fois sur une console pour un écran oublié coûte bien plus cher que dix
photos en trop.

---

## Règles générales

### Qualité

- Cadrer **droit**, l'écran bien à plat, sans perspective : un chiffre lu de biais se
  confond facilement (8/6, 3/8).
- Lumière indirecte, **pas de flash** : le reflet mange toujours la zone la plus utile.
- Désactiver la 3D sur 3DS avant de photographier.
- Zoomer plutôt que recadrer après coup, tant que la photo reste nette.
- **Vérifier la lisibilité sur place**, avant d'éteindre la console. Une photo floue
  découverte trois mois plus tard, c'est une console à rallumer.

### Ce qu'on cherche, sur n'importe quelle console

1. Rang de chasseur (HR / MR / rang de village)
2. Temps de jeu total, avec sa précision exacte telle qu'affichée (`HH:MM` ou heures)
3. Nombre de quêtes accomplies (et échouées si le jeu le distingue)
4. **Compteur de chasses par monstre** — la donnée la plus précieuse, et la plus
   souvent répartie sur plusieurs écrans à faire défiler
5. Usage par type d'arme, si le jeu le suit
6. Succès / trophées de la plateforme
7. Nom de chasseur, date de création de la sauvegarde si visible

### Captures numériques quand c'est possible

| Plateforme | Méthode | Qualité |
|---|---|---|
| Nintendo 3DS | photo au téléphone uniquement | dégradée, inévitable |
| Nintendo Switch | bouton Capture, puis microSD ou envoi vers smartphone | parfaite |
| PlayStation 4 | bouton SHARE, puis clé USB ou application PS | parfaite |
| Xbox | bouton de capture, puis application Xbox | parfaite |
| PC / Steam | touche de capture Steam, ou capture système | parfaite |

Privilégier systématiquement la capture numérique : elle est nette, datée, et évite
toute erreur de relecture. **Les 3DS sont donc les plus urgentes et les plus
laborieuses** — ce sont les seules où la photo est la seule option.

---

## Par jeu

Statut à remplir au fur et à mesure : `à faire` / `en cours` / `fait` / `n'existe pas`.

### `mh3u` — Monster Hunter 3 Ultimate (Nintendo 3DS)

| Écran | Ce qu'on y trouve | Statut |
|---|---|---|
| Guild Card, toutes les pages | rang, temps de jeu, quêtes | à faire |
| Liste des monstres / carnet | compteurs par monstre — **à vérifier : ce jeu les suit-il ?** | à faire |
| Équipement porté et coffre | armes et armures marquantes | à faire |
| Écran-titre / sélection de sauvegarde | nom, temps de jeu parfois affiché ici | à faire |

Point à trancher pendant la capture : si MH3U ne tient aucun compteur par monstre,
le noter explicitement — ce sera une lacune à documenter sur `/about/`, pas un trou
à combler par estimation.

### `mh4u` — Monster Hunter 4 Ultimate (Nintendo 3DS)

**À capturer en premier.** C'est le jeu retenu pour la phase 2, et sa Guild Card est
la plus riche du lot : elle sert de cas de référence pour le modèle de données.

| Écran | Ce qu'on y trouve | Statut |
|---|---|---|
| Guild Card, toutes les pages | rang, temps de jeu, quêtes, usage par arme | à faire |
| Carnet du chasseur / liste des monstres | compteurs de chasse par monstre | à faire |
| Palmarès / records de quêtes | si présent | à faire |
| Équipement et armes favorites | contexte pour les notes personnelles | à faire |

### `mhgu` — Monster Hunter Generations Ultimate (Nintendo Switch)

Capture numérique disponible : privilégier le bouton Capture.

| Écran | Ce qu'on y trouve | Statut |
|---|---|---|
| Guild Card, toutes les pages | rang, temps de jeu, quêtes, usage par arme | à faire |
| Carnet du chasseur / liste des monstres | compteurs de chasse | à faire |
| Styles de chasse et arts de chasse | spécifique à ce titre, à noter en prose | à faire |
| Profil utilisateur Switch | temps de jeu vu par la console, à croiser | à faire |

Le temps de jeu affiché par la console Switch et celui affiché par le jeu diffèrent
souvent (menus, veille). Capturer les deux et **choisir celui du jeu** comme valeur
de référence, en notant l'écart dans `notes`.

### `mhw` — Monster Hunter: World (PlayStation 4)

| Écran | Ce qu'on y trouve | Statut |
|---|---|---|
| Profil de chasseur | HR, MR, temps de jeu, quêtes | à faire |
| Carnet de terrain, fiche par monstre | chassés / capturés, niveau de recherche, couronnes | à faire |
| Liste des trophées PSN | jalons datés — utile pour la timeline | à faire |
| Équipement et set favori | contexte | à faire |

Le carnet de terrain distingue **chassés** et **capturés** : c'est le jeu qui justifie
la colonne `captured` du modèle. Le parcourir monstre par monstre est long — prévoir
une session dédiée.

Les trophées PSN sont datés : c'est la seule source d'horodatage réel du projet.
Précieux pour la timeline de carrière.

### `mhrise` — Monster Hunter Rise (Xbox Game Pass)

Préciser d'abord s'il s'agit du **Game Pass console** ou **PC** : la méthode de
capture et l'accès aux succès en dépendent.

| Écran | Ce qu'on y trouve | Statut |
|---|---|---|
| Profil de chasseur / Guild Card | rang village, HR, temps de jeu, quêtes | à faire |
| Carnet du chasseur, liste des monstres | compteurs de chasse | à faire |
| Succès Xbox | jalons datés | à faire |
| Équipement | contexte | à faire |

Attention : Rise étant sorti sur plusieurs plateformes, vérifier qu'il n'existe pas
une seconde sauvegarde ailleurs (Switch, Steam). Si oui, ce sont **deux entrées
distinctes** dans le modèle, pas une somme — les fusionner inventerait une
progression qui n'a jamais existé sur une seule sauvegarde.

### `mhwilds` — Monster Hunter Wilds (Steam)

Pas encore commencé. Contrairement aux autres, ce jeu est **évolutif** : ses stats
bougeront.

| Élément | Méthode | Statut |
|---|---|---|
| Temps de jeu | API Steam `IPlayerService/GetOwnedGames`, automatisable | phase 5 |
| Succès | API Steam `ISteamUserStats/GetPlayerAchievements`, automatisable | phase 5 |
| Compteurs par monstre | **non exposé par Steam** — capture in-game manuelle | manuel |

Limite structurante : Steam ne donnera jamais « 247 Rathalos ». Ce détail vit dans la
sauvegarde locale du jeu. La parser serait possible mais laborieux, et hors périmètre
tant que le reste n'est pas fait.

Pour ce jeu, prendre l'habitude de capturer le carnet à intervalle régulier (fin de
chaque phase de jeu) : c'est la seule façon d'avoir une progression datée.

---

## Nommage et rangement

### Photos brutes — hors du repo

```
C:\Users\loris\Documents\MH-career-sources\
├── mh3u\
├── mh4u\
│   ├── guild-card-p1.jpg
│   ├── guild-card-p2.jpg
│   ├── hunter-notes-01.jpg
│   └── hunter-notes-02.jpg
└── ...
```

Convention : `<type>-<index>.jpg`, index sur 2 chiffres, types stables :
`guild-card`, `hunter-notes`, `hunting-log`, `profile`, `achievements`, `gear`.

**Au moins deux copies**, dont une hors de la machine (disque externe ou cloud).
Ce dossier n'est pas versionné : il n'a aucun filet de sécurité par défaut.

### Versions réduites — commitées

```
static/sources/<game_id>/<même nom>.jpg
```

Cible : ~1600 px de large, ~200 Ko. Référencées depuis le champ `image` des blocs
`[[sources]]` de chaque `meta.toml`.

> **Étape manuelle assumée.** Le redimensionnement ne peut pas être automatisé ici :
> la bibliothèque standard Python ne sait pas traiter d'images, et ajouter une
> dépendance comme Pillow contredirait la règle « stdlib uniquement » qui fonde toute
> la chaîne. Le faire à la main avec n'importe quel visualiseur d'images est
> largement suffisant pour quelques dizaines de fichiers. Si le volume devenait tel
> que ça pose problème, c'est un des rares cas où une dépendance serait défendable —
> à rediscuter à ce moment-là, pas avant.

### Vie privée — le repo est public

Les Guild Cards affichent le nom de chasseur, parfois un identifiant en ligne ou un
code ami. **Recadrer ou masquer ces zones avant de commiter la version réduite.** La
photo brute, elle, reste hors repo et peut être conservée intacte.

Rappel : une image commitée puis supprimée reste dans l'historique git. La vérifier
avant, pas après.

---

## Suivi

| Jeu | Photos prises | Lisibilité vérifiée | Réduites et commitées | Saisie faite |
|---|---|---|---|---|
| `mh4u` | ☐ | ☐ | ☐ | ☐ |
| `mh3u` | ☐ | ☐ | ☐ | ☐ |
| `mhgu` | ☐ | ☐ | ☐ | ☐ |
| `mhw` | ☐ | ☐ | ☐ | ☐ |
| `mhrise` | ☐ | ☐ | ☐ | ☐ |
| `mhwilds` | ☐ | ☐ | ☐ | ☐ |

Ordre conseillé : `mh4u` d'abord (c'est le jeu de référence de la phase 2), puis les
3DS restantes tant que le matériel fonctionne, puis les plateformes à capture
numérique qui peuvent attendre sans risque.
