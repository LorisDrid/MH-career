# Illustrations des fiches de jeux

## Choix de présentation

Les captures personnelles fournissent les personnages, armures, poses et compagnons. Le Rathalos de l’accueil sert uniquement de référence de style. Le critère est la reconnaissance du personnage du joueur : une illustration générique du monstre emblématique aurait davantage identifié le titre, mais perdu ce lien personnel.

Une même image est utilisée en bandeau de fiche et dans sa carte de collection pour conserver une identité cohérente. Des images distinctes permettraient des cadrages optimisés, au prix de fichiers et de variantes supplémentaires. Les aperçus de collection se chargent à la demande (`loading="lazy"`).

Les associations jeu → illustration sont dans `config.toml`, sous `extra.game_art`, car il s’agit d’habillage éditorial propre au site. Les mettre dans le modèle statistique aurait permis de les exporter avec les données, mais aurait mélangé présentation et archive. Les templates se limitent à vérifier la présence d’une association et à l’afficher.

Les originaux restent dans le dossier personnel, inchangés. Les nouveaux PNG sont des illustrations interprétées par IA, jamais des preuves de statistiques. Les pages l’indiquent dans leur légende. Aucun portrait de chasseur n’est visible dans les captures de Rise examinées : son illustration reprend les deux compagnons dont les portraits sont présents. Aucune ressource World ou Wilds n’a été trouvée dans le dossier fourni ; leurs cartes gardent le traitement sans illustration.

## Génération

Outil : ImageGen intégré. Date : 16 septembre 2026. Les chemins ci-dessous documentent les références ; le site ne lit que les nouvelles images dans `static/images/`.

### mh3u

Fichier livré : `static/images/mh3u-guild.png`.

Références, dans l’ordre :

- `C:/Users/loris/Documents/MH/MH3U/20260915_122623.jpg`
- `C:/Users/loris/Documents/Programming/Github/MH-career/static/images/rathalos-hero.png`

Prompt exact :

Use case: style-transfer. Create a landscape 1536x1024 illustration for the header of a personal Monster Hunter archive, based on the supplied actual guild-card reference(s). Last image is ONLY a style reference: match its dark hand-inked engraved concept-art treatment, charcoal edges, copper and parchment highlights, intricate armor shading, painterly depth. Do NOT copy its Rathalos or its anonymous hunter. Preserve the reference character armor silhouettes, equipment colors, companions and recognizable pose rather than replacing them with generic fantasy characters. Remove screen hardware, UI, text, menus, stats, pixel grid, moire and reflections. This is an artistic reinterpretation of the personal game character, NOT a screenshot restoration. Composition: all characters grouped across the right half, visible from head to boots, upper heads around 25% height; quiet nearly black #0c0a09 LEFT 42% for HTML title. Fade smoothly into dark edges. Rich dramatic warm rim lighting, clear readable subjects with more light on them than background. No text, numbers, letters, logos, watermarks or borders. No additional monsters or human characters. Primary source is the MH3U photo: central hunter in bright gold/ochre plate armor, tall crest on closed helmet, black under-armor, silver knee plates, greeting with one raised arm. Retain the bulky jagged brown weapon visible behind the left shoulder. The two small masked Shakalaka companions flank the hunter: blue mask on left, pale green oval mask and tall staff on right. They are masked tribal companions, NOT cats. Preserve the joyful greeting composition, restage on a dark rocky ground with faint parchment field-journal motifs. Do not add dragons.

### mh4u

Fichier livré : `static/images/mh4u-guild.png`.

Références, dans l’ordre :

- `C:/Users/loris/Documents/MH/MH4U/20260915_124654.jpg`
- `C:/Users/loris/Documents/Programming/Github/MH-career/static/images/rathalos-hero.png`

Prompt exact :

Use case: style-transfer. Create a landscape 1536x1024 illustration for the header of a personal Monster Hunter archive, based on the supplied actual guild-card reference(s). Last image is ONLY a style reference: match its dark hand-inked engraved concept-art treatment, charcoal edges, copper and parchment highlights, intricate armor shading, painterly depth. Do NOT copy its Rathalos or its anonymous hunter. Preserve the reference character armor silhouettes, equipment colors, companions and recognizable pose rather than replacing them with generic fantasy characters. Remove screen hardware, UI, text, menus, stats, pixel grid, moire and reflections. This is an artistic reinterpretation of the personal game character, NOT a screenshot restoration. Composition: all characters grouped across the right half, visible from head to boots, upper heads around 25% height; quiet nearly black #0c0a09 LEFT 42% for HTML title. Fade smoothly into dark edges. Rich dramatic warm rim lighting, clear readable subjects with more light on them than background. No text, numbers, letters, logos, watermarks or borders. No additional monsters or human characters. Primary source photo is sideways: mentally rotate it 90 degrees COUNTERCLOCKWISE to restore upright standing hunter and horizontal ground. Preserve hunter in pale yellow/ivory/gold armor with red cloth at neck and waist, bare face beneath pale head gear, triumphant raised bent fist. Preserve both upright feline companions flanking the hunter (pale cream cat in light outfit at left, stout cat in green hood and brown outfit at right). Suggest the warm orange sky and airship/mechanical deck of the source, darkened into the website backdrop. All characters must stand upright. Do not add dragons.

### mhgen

Fichier livré : `static/images/mhgen-guild.png`.

Références, dans l’ordre :

- `C:/Users/loris/Documents/MH/MHGenerations/20260915_130017.jpg`
- `C:/Users/loris/Documents/Programming/Github/MH-career/static/images/rathalos-hero.png`

Prompt exact :

Use case: style-transfer. Create a landscape 1536x1024 illustration for the header of a personal Monster Hunter archive, based on the supplied actual guild-card reference(s). Last image is ONLY a style reference: match its dark hand-inked engraved concept-art treatment, charcoal edges, copper and parchment highlights, intricate armor shading, painterly depth. Do NOT copy its Rathalos or its anonymous hunter. Preserve the reference character armor silhouettes, equipment colors, companions and recognizable pose rather than replacing them with generic fantasy characters. Remove screen hardware, UI, text, menus, stats, pixel grid, moire and reflections. This is an artistic reinterpretation of the personal game character, NOT a screenshot restoration. Composition: all characters grouped across the right half, visible from head to boots, upper heads around 25% height; quiet nearly black #0c0a09 LEFT 42% for HTML title. Fade smoothly into dark edges. Rich dramatic warm rim lighting, clear readable subjects with more light on them than background. No text, numbers, letters, logos, watermarks or borders. No additional monsters or human characters. Primary source is the Generations photograph: hunter wearing unmistakable angular dark blue-black and crimson spiked armor with a tall jagged horned full helmet, both arms opened in a confident greeting, red segmented legs. Two small Palico cats at their side, one in gold armor and the other pale blue/gray armor, preserve the reference designs. Retain the enormous curved rib-like background forms and muted blue atmosphere as a subtle backdrop, no extra monsters. Group hunter and both cats on right with a full-body heroic composition.

### mhrise

Fichier livré : `static/images/mhrise-guild.png`.

Références, dans l’ordre :

- `C:/Users/loris/Documents/MH/MHRise/Capture d'écran 2026-09-15 142136.png`
- `C:/Users/loris/Documents/MH/MHRise/Capture d'écran 2026-09-15 142149.png`
- `C:/Users/loris/Documents/Programming/Github/MH-career/static/images/rathalos-hero.png`

Prompt exact :

Use case: style-transfer. Create a landscape 1536x1024 illustration for the header of a personal Monster Hunter archive, based on the supplied actual guild-card reference(s). Last image is ONLY a style reference: match its dark hand-inked engraved concept-art treatment, charcoal edges, copper and parchment highlights, intricate armor shading, painterly depth. Do NOT copy its Rathalos or its anonymous hunter. Preserve the reference character armor silhouettes, equipment colors, companions and recognizable pose rather than replacing them with generic fantasy characters. Remove screen hardware, UI, text, menus, stats, pixel grid, moire and reflections. This is an artistic reinterpretation of the personal game character, NOT a screenshot restoration. Composition: all characters grouped across the right half, visible from head to boots, upper heads around 25% height; quiet nearly black #0c0a09 LEFT 42% for HTML title. Fade smoothly into dark edges. Rich dramatic warm rim lighting, clear readable subjects with more light on them than background. No text, numbers, letters, logos, watermarks or borders. No additional monsters or human characters. First screenshot supplies the canine Palamute only: gray and white face, tall pointed ears with tan protective headgear, layered green feather-like cape, leather harness and leggings. Second screenshot supplies the small Palico only: orange-red feline helmet with gold detailing, red/brown round armor, white paws and black/white legs. Make a beautifully illustrated portrait of THESE TWO companions together, confident upright Palamute at right and small Palico beside it. Preserve actual character designs, no invented human hunter because none is visible in these references. Restage them on a dark quiet ground with faint Japanese brushwork mist. Do not depict any UI or writing from the screenshots.

