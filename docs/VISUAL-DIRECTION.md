# Direction visuelle — carnet de guilde

## Choix

- **Carte de guilde sombre, illustration de Rathalos et ornements anguleux** : le critère dominant est la reconnaissance immédiate de Monster Hunter. Un carnet entièrement parcheminé aurait renforcé la matière et le côté ancien, au prix de tableaux plus chargés.
- **Deux statistiques principales, puis trois secondaires** : priorité au temps de jeu et aux chasses. Une grille uniforme aurait facilité la comparaison de compteurs de même importance, mais aucun ne se serait distingué.
- **Cartes partagées entre l’accueil et la collection** : le critère est la cohérence des fiches et la mise en valeur des jeux. Un tableau reste plus compact pour comparer beaucoup de colonnes ; il est conservé dans le bestiaire et les armes.
- **Polices système** : priorité à un rendu disponible sans installation ni requêtes manquantes. Les cinq fichiers de polices personnalisées prévus ne sont pas présents. Des polices auto-hébergées offriraient une identité plus précise une fois les fichiers fournis.
- **Illustration PNG locale, emblème SVG décoratif et CSS sans dépendance** : priorité à l’autonomie du site. Une image distante réduirait la taille du dépôt, mais introduirait une dépendance à un tiers à chaque visite. Le PNG préserve le résultat généré sans outil supplémentaire ; un WebP serait plus léger si une conversion était organisée ultérieurement.

La palette de données est conservée. Les contrastes des textes sur les panneaux ont été recalculés dans la feuille de style. Les dates et statistiques proviennent exclusivement du pipeline existant ; l’image ne constitue pas une source de données.

## Illustration

- Fichier : `static/images/rathalos-hero.png`.
- Origine : illustration générée par l’outil intégré ImageGen le 16 septembre 2026, pour ce site personnel ; ce n’est pas une illustration officielle.
- L’emblème `static/images/guild-mark.svg` est un dessin décoratif original, pas le logo officiel de la guilde.

### Prompt exact

Use case: stylized-concept. Asset type: wide background illustration for a personal Monster Hunter guild card website, landscape 1536x1024. Subject: unmistakable Rathalos from Monster Hunter, red armored wyvern with spiked head, powerful hind legs and enormous membranous wings, side three-quarter view looming over a tiny armored hunter carrying a great sword, on a rocky ridge. Composition: Rathalos occupies right two thirds, head near upper right center, wing spread dramatically across top, hunter near lower center right. Left third quiet deep charcoal negative space for HTML title. Style: sophisticated hand-inked hunter field journal illustration mixed with richly shaded vintage game concept art, crisp silhouette, weathered engraved lines, restrained parchment gold and oxidized copper/red pigments, muted desaturated forest in distant haze, very dark charcoal background #0c0a09. Atmospheric, majestic, adventurous, detailed and recognizable Monster Hunter anatomy. No lettering, no text, no logos, no UI, no numbers, no frame, no watermark. Dark edges that blend with website background; warm ivory highlights on monster face and wing edges. It must feel like an actual Monster Hunter bestiary artwork, not a generic medieval dragon.

