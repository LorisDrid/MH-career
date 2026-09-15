"""Exports plats, pour analyse au tableur.

Les sources restent decoupees par jeu : une erreur de saisie sur un jeu ne peut
alors pas en corrompre un autre, et l'historique git reste lisible par jeu. Mais
l'analyse, elle, veut une table unique au format long (une ligne par observation,
le jeu en colonne). Ces fichiers la produisent.

Ils sont GENERES : comme tout data/generated/, ils ne s'editent jamais a la main.
Pour corriger une valeur, on corrige la source et on relance le build.
"""
from __future__ import annotations

import csv
from pathlib import Path

from tools.aggregate import game_order
from tools.model import GameData, Reference

HUNTS_COLUMNS = (
    "game", "game_title", "monster_id", "monster_fr",
    "base_form", "variant_type", "hunted", "captured", "notes",
)
WEAPONS_COLUMNS = ("game", "game_title", "weapon_id", "weapon_fr", "uses", "notes")


def _cell(value: int | None) -> str:
    """None reste une cellule VIDE : la distinction inconnu / zero survit a l'export."""
    return "" if value is None else str(value)


def _writer(path: Path, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    # utf-8-sig : sans BOM, un tableur sous Windows affiche les accents de
    # travers. Ces fichiers n'existent que pour etre ouverts a la main.
    handle = path.open("w", newline="", encoding="utf-8-sig")
    writer = csv.writer(handle, lineterminator="\n")
    writer.writerow(columns)
    return handle, writer


def write_hunts(path: Path, ref: Reference, games: dict[str, GameData]) -> int:
    handle, writer = _writer(path, HUNTS_COLUMNS)
    count = 0
    with handle:
        for game_id in game_order(ref):
            data = games.get(game_id)
            if data is None:
                continue
            title = ref.games[game_id].short_title
            for hunt in data.hunts:
                monster = ref.monsters.get(hunt.monster_id)
                writer.writerow([
                    game_id,
                    title,
                    hunt.monster_id,
                    monster.name_fr if monster else "",
                    monster.base if monster and monster.base else hunt.monster_id,
                    monster.variant_type if monster and monster.variant_type else "",
                    _cell(hunt.hunted),
                    _cell(hunt.captured),
                    hunt.notes or "",
                ])
                count += 1
    return count


def write_weapons(path: Path, ref: Reference, games: dict[str, GameData]) -> int:
    handle, writer = _writer(path, WEAPONS_COLUMNS)
    count = 0
    with handle:
        for game_id in game_order(ref):
            data = games.get(game_id)
            if data is None:
                continue
            title = ref.games[game_id].short_title
            for use in data.weapon_uses:
                weapon = ref.weapons.get(use.weapon_id)
                writer.writerow([
                    game_id,
                    title,
                    use.weapon_id,
                    (weapon.name_fr or weapon.name_en) if weapon else "",
                    _cell(use.uses),
                    use.notes or "",
                ])
                count += 1
    return count


def write_all(root: Path, ref: Reference, games: dict[str, GameData]) -> dict[str, int]:
    base = root / "data" / "generated"
    return {
        "hunts-all.csv": write_hunts(base / "hunts-all.csv", ref, games),
        "weapons-all.csv": write_weapons(base / "weapons-all.csv", ref, games),
    }
