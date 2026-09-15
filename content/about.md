+++
title = "Méthodologie"
template = "page.html"
weight = 90
+++

Ce site n'affiche que des chiffres relevés sur les écrans des jeux eux-mêmes.
Aucune valeur n'est estimée, déduite ou complétée.

## Comment lire les tableaux

Deux notations qui ne veulent **pas** dire la même chose :

- **—** signifie *inconnu* : le jeu n'affichait pas ce compteur, ou il n'a pas
  encore été relevé.
- **0** signifie *zéro constaté* : le compteur existait bien et affichait zéro.

Confondre les deux serait la façon la plus simple de corrompre cette archive.
Toute la chaîne technique, du fichier source jusqu'au rendu, maintient la
distinction.

## D'où viennent les chiffres

Chaque jeu expose des compteurs différents, et aucun schéma commun ne leur est
imposé : un champ absent d'un jeu reste absent, plutôt que d'être comblé.

Les relevés proviennent de photographies des Guild Cards et carnets de chasseur,
prises console en main. Chaque jeu déclare ses sources et leur date de capture.

## Lacunes connues

**MH3U — six chasses non attribuables.** Le Journal monstre affiche `????` à la
place du *nom* sur cinq lignes, alors que la taille et le compteur de chasses,
eux, sont bien renseignés. Ces six chasses ne sont donc rattachables à aucun
monstre : plutôt que d'inventer une entrée, elles sont laissées de côté. Le total
MH3U affiché sur ce site est en conséquence inférieur de 6 à celui de la console.

**MH4U — date de début inconnue.** Le journal de chasse ne conserve que les
sessions récentes. On sait quand la partie s'est arrêtée, pas quand elle a
commencé.

**Espèces des monstres.** Aucune Guild Card n'affiche l'espèce d'un monstre.
La renseigner supposerait une source extérieure au jeu, ce que ce projet
s'interdit ; le champ reste donc vide tant qu'il n'a pas été vérifié.

## Ce que ce site ne peut pas dire

Aucun jeu Monster Hunter n'enregistre la date d'une chasse individuelle. Les
repères temporels — « premier Rathalos en telle année » — se déduisent de la
période pendant laquelle le jeu a été joué, pas d'un horodatage réel. C'est une
approximation, assumée comme telle.

Les compteurs d'usage des armes ne se comparent pas d'un jeu à l'autre : leur
définition varie selon les titres. Leur agrégation produit un classement, jamais
un total.
