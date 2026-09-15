# Données brutes, un dossier par jeu

Ce dossier est vide tant qu'aucun jeu n'a été saisi. Pour ajouter un jeu, créer
`data/games/<game_id>/` où `<game_id>` correspond **exactement** à une entrée de
`data/reference/games.toml`, puis y placer :

| Fichier | Contenu | Obligatoire |
|---|---|---|
| `meta.toml` | rang, temps de jeu, quêtes, et les blocs `[[sources]]` | dès qu'il y a une valeur |
| `hunts.csv` | `monster_id,hunted,captured,notes` | recommandé |
| `weapons.csv` | `weapon_id,uses,notes` | si le jeu suit l'usage des armes |

Deux règles à ne pas perdre de vue :

- **Cellule vide = inconnu. `0` = zéro constaté.** Ne jamais mettre `0` pour
  combler un trou : le validateur ne peut pas rattraper cette erreur-là, c'est
  la seule qui corrompt les données en silence.
- **Tout `monster_id` doit exister dans `data/reference/monsters.toml`.** Le
  référentiel se complète au fur et à mesure, monstre par monstre.

Le format complet est décrit dans [../../docs/DATA-MODEL.md](../../docs/DATA-MODEL.md).
Lancer `python -m tools.build --check` après chaque saisie : toutes les erreurs
sont rapportées d'un coup, avec fichier, ligne et suggestion.
