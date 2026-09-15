"""Calculs inter-jeux et construction de site.json.

Toute la logique metier vit ici, jamais dans les templates (AGENTS.md 4) : Zola
ne fait que du rendu, ce qui rend cette agregation testable en isolation et Zola
remplacable.
"""
from __future__ import annotations

import statistics
from datetime import datetime, timezone
from pathlib import Path

from tools.model import WEAPON_IDS, GameData, Progress, Reference

SCHEMA_VERSION = 1


def sum_or_none(values) -> int | None:
    """Somme les valeurs connues, mais renvoie None si AUCUNE ne l'est.

    C'est la fonction la plus importante du projet. Un sum() nu renverrait 0
    sur une liste entierement inconnue, ce qui affirmerait "zero chasse"
    la ou la verite est "on ne sait pas". Sur une archive, cette confusion
    est une corruption de donnee.
    """
    known = [v for v in values if v is not None]
    return sum(known) if known else None


def coarsest_precision(precisions) -> str | None:
    """Un total ne peut pas etre plus precis que son terme le plus grossier."""
    known = [p for p in precisions if p is not None]
    if not known:
        return None
    return "hours" if "hours" in known else "minutes"


def precision_label(precision: str | None) -> str | None:
    """Libelle affichable de la precision, ou None quand il n'y a rien a dire.

    La cle technique ("hours") ne doit jamais atteindre l'ecran : elle est en
    anglais et n'explique rien. Une duree relevee a la minute n'appelle aucune
    mention ; seule une valeur arrondie merite d'etre signalee.
    """
    return "arrondi à l'heure" if precision == "hours" else None


def format_playtime(minutes: int | None, precision: str | None) -> str | None:
    """Rend une duree pour l'affichage, en respectant sa precision reelle.

    Formater ici plutot que dans le template applique la regle "aucun calcul
    dans Tera" (AGENTS.md 4), et surtout centralise la precision : une valeur
    arrondie a l'heure ne doit jamais s'afficher avec des minutes, sous peine
    de suggerer une exactitude qui n'existe pas.
    """
    if minutes is None:
        return None
    hours, remainder = divmod(minutes, 60)
    if precision == "hours":
        return f"{hours} h"
    return f"{hours} h {remainder:02d}"


MATRIX_BINS = 5

# Libellés français des catégories d'armes. L'identifiant reste la clé stable du
# référentiel ; seule la présentation est traduite, et elle l'est ici parce que
# les templates ne calculent rien.
CATEGORY_FR = {"melee": "Mêlée", "ranged": "Distance", "special": "Spécial"}

MONTHS_FR = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet",
             "août", "septembre", "octobre", "novembre", "décembre")


def month_label(value: str | None) -> str | None:
    """« 2016-07 » -> « juillet 2016 ».

    Le format ISO reste la forme stockée : il se trie, il est sans ambiguïté et
    il ne suppose aucune langue. Ce n'est pas pour autant une forme lisible, et
    la conversion se fait ici parce que les templates ne calculent rien.
    """
    if not value:
        return None
    parts = value.split("-")
    if len(parts) != 2:
        return value
    year, month = parts
    if not (month.isdigit() and 1 <= int(month) <= 12):
        return value
    return f"{MONTHS_FR[int(month) - 1]} {year}"


def quantile_edges(values, bins: int = MATRIX_BINS) -> list[int]:
    """Bornes de paliers decoupees par quantiles, et non lineairement.

    La distribution des chasses est tres dissymetrique : 123 pour Grand Jaggi,
    1 pour pres de la moitie du bestiaire. Un decoupage lineaire tasserait tout
    dans le premier palier et la matrice ne dirait plus rien. Les quantiles
    repartissent les monstres sur toute la rampe.
    """
    known = sorted(v for v in values if v)
    if len(known) < bins:
        return sorted(set(known))[:-1]
    cuts = statistics.quantiles(known, n=bins, method="inclusive")
    # Des bornes identiques produiraient des paliers vides : on les fusionne.
    return sorted({int(cut) for cut in cuts})


def level_of(value: int | None, edges: list[int]) -> int | None:
    """Palier de teinte, ou None pour un inconnu COMME pour un zero constate.

    Un zero n'est pas teinte : la cellule affiche `0` sur fond neutre, et
    l'inconnu affiche un tiret sur le meme fond. C'est le TEXTE qui porte la
    distinction, la couleur ne porte que la magnitude — la teinter reviendrait
    a encoder deux choses sur un seul canal.
    """
    if not value:
        return None
    return sum(1 for edge in edges if value > edge)


def scale_labels(edges: list[int]) -> list[str]:
    """Intitules des paliers, pour que la legende annonce des intervalles REELS.

    Une rampe sans echelle ne se lit pas : le lecteur voit des nuances sans
    savoir ce qu'elles valent. Calcule ici et non dans le template, ou aucun
    calcul n'a sa place.
    """
    if not edges:
        return []
    labels, low = [], 1
    for edge in edges:
        labels.append(str(low) if low == edge else f"{low}–{edge}")
        low = edge + 1
    labels.append(f"{low}+")
    return labels


def fraction(value: int | None, maximum: int | None) -> float | None:
    """Part de la valeur maximale, pour piloter la longueur d'une barre.

    Lineaire a dessein : la longueur d'une barre doit rester proportionnelle a
    la valeur. Une echelle compressee rendrait la longue traine plus lisible au
    prix d'un mensonge sur les proportions.
    """
    if value is None or not maximum or maximum <= 0:
        return None
    return round(value / maximum, 4)


def game_order(ref: Reference):
    """Ordre chronologique de carriere, avec repli sur la generation."""

    def key(game_id: str):
        game = ref.games[game_id]
        return (
            game.played_from is None,
            game.played_from or "",
            game.generation if game.generation is not None else 99,
            game.title,
        )

    return sorted(ref.games, key=key)


def _hunts_by_monster(data: GameData) -> dict[str, tuple[int | None, int | None]]:
    return {h.monster_id: (h.hunted, h.captured) for h in data.hunts}


def _base_form(ref: Reference, monster_id: str) -> str:
    monster = ref.monsters.get(monster_id)
    if monster is None or monster.base is None:
        return monster_id
    return monster.base


def build_games(ref: Reference, games: dict[str, GameData]) -> list[dict]:
    payload: list[dict] = []
    for game_id in game_order(ref):
        game = ref.games[game_id]
        data = games.get(game_id)
        platform = ref.platforms.get(game.platform)
        # Toujours emettre le jeu complet de champs, meme sans donnee : la
        # FORME du document ne doit pas dependre de la presence de valeurs.
        # Tera evalue les arguments de macro avant tout filtre, donc une cle
        # absente casse le rendu la ou un None s'affiche proprement en tiret.
        progress = vars(data.progress if data else Progress()).copy()
        progress["playtime_display"] = format_playtime(
            progress.get("playtime_minutes"), progress.get("playtime_precision")
        )
        # Total derive de la ventilation affichee, jamais saisi (voir Progress).
        quests = progress.get("quests") or {}
        progress["quests_total"] = sum(quests.values()) if quests else None
        progress["playtime_note"] = precision_label(progress.get("playtime_precision"))

        hunts = data.hunts if data else []
        ranked = sorted(
            ({"id": h.monster_id,
              "name_fr": ref.monsters[h.monster_id].name_fr
              if h.monster_id in ref.monsters else h.monster_id,
              "hunted": h.hunted}
             for h in hunts if h.hunted),
            key=lambda row: -row["hunted"],
        )

        payload.append({
            "id": game_id,
            "title": game.title,
            "short_title": game.short_title,
            "platform": game.platform,
            "platform_name": platform.name if platform else game.platform,
            "generation": game.generation,
            "released": game.released,
            "played_from": month_label(game.played_from),
            "played_to": month_label(game.played_to),
            "status": game.status,
            "has_data": data is not None and (data.has_progress or bool(hunts)),
            "progress": progress,
            "sources": [vars(s) for s in data.sources] if data else [],
            # Aucune ligne de chasse ne veut pas dire « zéro monstre » : cela
            # veut dire que le bestiaire de ce jeu n'a pas encore été relevé.
            # Afficher 0 ici, à côté de deux tirets, inverserait la convention
            # que tout le reste de la chaîne s'applique à tenir.
            "monsters_recorded": len(hunts) if hunts else None,
            "total_hunted": sum_or_none(h.hunted for h in hunts),
            "total_captured": sum_or_none(h.captured for h in hunts),
            "top_monsters": ranked[:5],
        })

    # Barres du tableau des jeux, et barres des monstres les plus chasses de
    # chaque fiche. Normalisees separement : comparer un jeu a un monstre
    # n'aurait aucun sens.
    top_game = max((row["total_hunted"] or 0) for row in payload) if payload else 0
    for row in payload:
        row["bar"] = fraction(row["total_hunted"], top_game)
        top_monster = max((m["hunted"] or 0) for m in row["top_monsters"])             if row["top_monsters"] else 0
        for monster in row["top_monsters"]:
            monster["bar"] = fraction(monster["hunted"], top_monster)
    return payload


def build_bestiary(ref: Reference, games: dict[str, GameData]) -> list[dict]:
    """Regroupe chaque variante sous sa forme de base.

    C'est ce regroupement qui permet de repondre a "combien de Rathalos, toutes
    formes confondues", tout en conservant le detail par forme.
    """
    per_game = {gid: _hunts_by_monster(data) for gid, data in games.items()}
    recorded = {mid for table in per_game.values() for mid in table}
    if not recorded:
        return []

    groups: dict[str, list[str]] = {}
    for monster_id in recorded:
        groups.setdefault(_base_form(ref, monster_id), []).append(monster_id)

    # Matrice complete : chaque ligne du bestiaire porte une valeur pour CHAQUE
    # jeu saisi, quitte a ce qu'elle soit None. Sans cela, les templates
    # devraient gerer des cles absentes, ce qui reintroduirait de la logique
    # dans Tera.
    matrix = [gid for gid in game_order(ref) if gid in per_game]
    bestiary: list[dict] = []
    for base_id, form_ids in groups.items():
        base = ref.monsters.get(base_id)
        form_ids = sorted(form_ids, key=lambda m: (m != base_id, m))

        game_totals = {
            gid: sum_or_none(per_game[gid].get(mid, (None, None))[0] for mid in form_ids)
            for gid in matrix
        }
        appeared = [gid for gid, total in game_totals.items() if total]

        bestiary.append({
            "id": base_id,
            "name_fr": base.name_fr if base else base_id,
            "name_en": base.name_en if base else base_id,
            "species": base.species if base else None,
            "total_hunted": sum_or_none(game_totals.values()),
            "total_captured": sum_or_none(
                per_game[gid].get(mid, (None, None))[1]
                for gid in per_game for mid in form_ids
            ),
            "per_game": game_totals,
            "first_game": appeared[0] if appeared else None,
            "last_game": appeared[-1] if appeared else None,
            "forms": [
                {
                    "id": mid,
                    "name_fr": ref.monsters[mid].name_fr if mid in ref.monsters else mid,
                    "variant_type": ref.monsters[mid].variant_type
                    if mid in ref.monsters else None,
                    "total_hunted": sum_or_none(
                        per_game[gid].get(mid, (None, None))[0] for gid in per_game
                    ),
                }
                for mid in form_ids
            ],
        })

    bestiary.sort(key=lambda row: (row["total_hunted"] is None,
                                   -(row["total_hunted"] or 0),
                                   row["name_fr"]))

    edges = quantile_edges(v for row in bestiary for v in row["per_game"].values())
    top = max((row["total_hunted"] or 0) for row in bestiary)
    for row in bestiary:
        row["per_game_level"] = {
            gid: level_of(value, edges) for gid, value in row["per_game"].items()
        }
        row["bar"] = fraction(row["total_hunted"], top)
    return bestiary


def build_weapons(ref: Reference, games: dict[str, GameData]) -> list[dict]:
    ordered_games = game_order(ref)
    uses = {
        gid: {u.weapon_id: u.uses for u in data.weapon_uses}
        for gid, data in games.items()
    }
    known_ids = [wid for wid in WEAPON_IDS if wid in ref.weapons]
    known_ids += [wid for wid in ref.weapons if wid not in WEAPON_IDS]

    payload: list[dict] = []
    for weapon_id in known_ids:
        weapon = ref.weapons[weapon_id]
        per_game = {gid: uses[gid].get(weapon_id) for gid in ordered_games if gid in uses}
        payload.append({
            "id": weapon_id,
            "name_en": weapon.name_en,
            "name_fr": weapon.name_fr,
            "category": CATEGORY_FR.get(weapon.category, weapon.category),
            "introduced": weapon.introduced,
            "per_game": per_game,
            # Nomme "score" et non "total" a dessein : la definition de `uses`
            # varie d'un jeu a l'autre, donc la somme est un classement, pas un
            # total comparable (voir docs/DATA-MODEL.md).
            "usage_score": sum_or_none(per_game.values()),
        })

    top = max((row["usage_score"] or 0) for row in payload) if payload else 0
    for row in payload:
        row["bar"] = fraction(row["usage_score"], top)
    return payload


def build_timeline(ref: Reference) -> list[dict]:
    events: list[dict] = []
    for game_id in game_order(ref):
        game = ref.games[game_id]
        if game.played_from:
            events.append({"date": game.played_from,
                           "date_label": month_label(game.played_from),
                           "game": game_id, "label": game.short_title,
                           "kind": "start", "kind_label": "première session"})
        if game.played_to:
            events.append({"date": game.played_to,
                           "date_label": month_label(game.played_to),
                           "game": game_id, "label": game.short_title,
                           "kind": "end", "kind_label": "dernière session"})
    return sorted(events, key=lambda e: e["date"])


def build_totals(ref: Reference, games: dict[str, GameData]) -> dict:
    progresses = [d.progress for d in games.values()]
    all_hunts = [h for d in games.values() for h in d.hunts]

    months = [g.played_from for g in ref.games.values() if g.played_from]
    months += [g.played_to for g in ref.games.values() if g.played_to]
    span = None
    if months:
        first, last = min(months), max(months)
        span = {
            "from": first,
            "to": last,
            "years": round((int(last[:4]) * 12 + int(last[5:7])
                            - int(first[:4]) * 12 - int(first[5:7])) / 12, 1),
        }

    playtime = sum_or_none(p.playtime_minutes for p in progresses)
    precision = coarsest_precision(
        p.playtime_precision for p in progresses if p.playtime_minutes is not None
    )

    return {
        # Les denombrements sont de vrais entiers : 0 jeu saisi, c'est 0, pas
        # "inconnu". Seules les SOMMES de valeurs potentiellement inconnues
        # peuvent valoir None.
        "games": len(ref.games),
        "games_with_data": sum(
            1 for d in games.values() if d.has_progress or d.hunts
        ),
        "monsters_recorded": len({h.monster_id for h in all_hunts}),
        "distinct_monsters_hunted": len(
            {h.monster_id for h in all_hunts if h.hunted}
        ),
        "playtime_minutes": playtime,
        "playtime_precision": precision,
        "playtime_display": format_playtime(playtime, precision),
        "playtime_note": precision_label(precision),
        "hunted": sum_or_none(h.hunted for h in all_hunts),
        "captured": sum_or_none(h.captured for h in all_hunts),
        "quests_total": sum_or_none(
            sum(p.quests.values()) if p.quests else None for p in progresses
        ),
        "career_span": span,
    }


def build_site(ref: Reference, games: dict[str, GameData]) -> dict:
    games_payload = build_games(ref, games)
    bestiary = build_bestiary(ref, games)
    return {
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "built_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        },
        "totals": build_totals(ref, games),
        "games": games_payload,
        # Indexe par id pour que la fiche d'un jeu se resolve par simple acces
        # cle depuis le slug de page, sans filtrage dans le template.
        "games_by_id": {row["id"]: row for row in games_payload},
        # Ordre des colonnes des tableaux croises : garanti identique aux cles
        # de `per_game` de chaque ligne du bestiaire et des armes.
        "matrix_games": [gid for gid in game_order(ref) if gid in games],
        "bestiary": bestiary,
        # Bornes des paliers, pour que la legende annonce des intervalles reels
        # plutot que des nuances sans echelle.
        "matrix_scale": scale_labels(
            quantile_edges(v for row in bestiary for v in row["per_game"].values())
        ),
        "weapons": build_weapons(ref, games),
        "timeline": build_timeline(ref),
    }
