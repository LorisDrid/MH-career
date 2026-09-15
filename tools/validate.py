"""Controles d'integrite des donnees.

Implemente la section "Controles de validation" de docs/DATA-MODEL.md.

Toute violation arrete le build (AGENTS.md 9) : sur un projet d'archivage, un
build qui passe quand meme en ignorant une donnee invalide est la pire issue
possible, parce que l'erreur devient invisible.

Les avertissements, eux, signalent une incoherence probable sans bloquer.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from tools.model import (
    GAME_STATUSES,
    PRECISIONS,
    SOURCE_KINDS,
    VARIANT_TYPES,
    WEAPON_IDS,
    GameData,
    Reference,
)
from tools.report import Report, suggest

ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")

REFERENCE_DIR = "data/reference"


def _check_id(entity_id: str, where: str, kind: str, report: Report) -> None:
    """Interdit notamment les tirets : dans Tera, a-b est une soustraction."""
    if not ID_RE.match(entity_id):
        report.error(
            where,
            f"{kind} '{entity_id}' : identifiant invalide, attendu snake_case "
            f"sans tiret ni accent (regle ^[a-z][a-z0-9_]*$)",
        )


def _check_reference_key(
    value: str | None, table: dict, where: str, label: str, report: Report,
    line: int | None = None,
) -> None:
    if value is None or value in table:
        return
    report.error(where, f"{label} '{value}' inconnu{suggest(value, table)}", line)


def _check_month(value: str | None, where: str, label: str, report: Report) -> date | None:
    if value is None:
        return None
    if not MONTH_RE.match(value):
        report.error(where, f"{label} : '{value}' attendu au format YYYY-MM")
        return None
    try:
        return date(int(value[:4]), int(value[5:7]), 1)
    except ValueError:
        report.error(where, f"{label} : '{value}' n'est pas un mois valide")
        return None


def _check_day(value: str | None, where: str, label: str, report: Report) -> date | None:
    if value is None:
        return None
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        report.error(where, f"{label} : '{value}' attendu au format YYYY-MM-DD")
        return None
    if parsed > date.today():
        report.error(where, f"{label} : '{value}' est dans le futur")
    return parsed


def _check_counter(
    value: int | None, where: str, label: str, line: int, report: Report
) -> None:
    if value is not None and value < 0:
        report.error(where, f"{label} : {value} est negatif", line)


def validate_reference(ref: Reference, root: Path, report: Report) -> None:
    for platform_id in ref.platforms:
        _check_id(platform_id, f"{REFERENCE_DIR}/platforms.toml", "plateforme", report)

    where = f"{REFERENCE_DIR}/games.toml"
    for game_id, game in ref.games.items():
        _check_id(game_id, where, "jeu", report)
        _check_reference_key(game.platform, ref.platforms, where,
                             f"'{game_id}' : platform", report)
        if game.status not in GAME_STATUSES:
            report.error(
                where,
                f"'{game_id}' : status '{game.status}' invalide, "
                f"attendu {' | '.join(GAME_STATUSES)}",
            )
        start = _check_month(game.played_from, where, f"'{game_id}' : played_from", report)
        end = _check_month(game.played_to, where, f"'{game_id}' : played_to", report)
        if start and end and start > end:
            report.error(
                where,
                f"'{game_id}' : played_from ({game.played_from}) est posterieur "
                f"a played_to ({game.played_to})",
            )

    for species_id in ref.species:
        _check_id(species_id, f"{REFERENCE_DIR}/species.toml", "espece", report)

    where = f"{REFERENCE_DIR}/monsters.toml"
    for monster_id, monster in ref.monsters.items():
        _check_id(monster_id, where, "monstre", report)
        _check_reference_key(monster.species, ref.species, where,
                             f"'{monster_id}' : species", report)
        _check_reference_key(monster.debut, ref.games, where,
                             f"'{monster_id}' : debut", report)
        if monster.base is not None:
            _check_reference_key(monster.base, ref.monsters, where,
                                 f"'{monster_id}' : base", report)
            parent = ref.monsters.get(monster.base)
            if parent is not None and parent.is_variant:
                report.error(
                    where,
                    f"'{monster_id}' : base '{monster.base}' est elle-meme une "
                    f"variante ; les chaines de variantes ne sont pas permises",
                )
            if monster.base == monster_id:
                report.error(where, f"'{monster_id}' : base pointe sur lui-meme")
        if (monster.base is None) != (monster.variant_type is None):
            report.error(
                where,
                f"'{monster_id}' : base et variant_type doivent etre presents "
                f"tous les deux ou absents tous les deux",
            )
        if monster.variant_type is not None and monster.variant_type not in VARIANT_TYPES:
            report.error(
                where,
                f"'{monster_id}' : variant_type '{monster.variant_type}' invalide, "
                f"attendu {' | '.join(VARIANT_TYPES)}",
            )

    where = f"{REFERENCE_DIR}/weapons.toml"
    for weapon_id, weapon in ref.weapons.items():
        _check_id(weapon_id, where, "arme", report)
        if weapon_id not in WEAPON_IDS:
            report.error(
                where,
                f"arme '{weapon_id}' hors des 14 types connus"
                f"{suggest(weapon_id, WEAPON_IDS)}",
            )
        _check_reference_key(weapon.introduced, ref.games, where,
                             f"'{weapon_id}' : introduced", report)
    if ref.weapons:
        for weapon_id in WEAPON_IDS:
            if weapon_id not in ref.weapons:
                report.warn(where, f"type d'arme absent du referentiel : '{weapon_id}'")


def validate_game_data(
    data: GameData, ref: Reference, root: Path, report: Report
) -> None:
    game_dir = f"data/games/{data.game_id}"
    meta = f"{game_dir}/meta.toml"
    progress = data.progress

    _check_reference_key(progress.primary_weapon, ref.weapons, meta,
                         "primary_weapon", report)

    for label, value in (
        ("hunter_rank", progress.hunter_rank),
        ("master_rank", progress.master_rank),
        ("village_rank", progress.village_rank),
        ("playtime_minutes", progress.playtime_minutes),
    ):
        if value is not None and value < 0:
            report.error(meta, f"{label} : {value} est negatif")

    if not isinstance(progress.quests, dict):
        report.error(meta, "quests doit etre une table categorie = nombre")
    else:
        for category, value in progress.quests.items():
            if not ID_RE.match(category):
                report.error(
                    meta,
                    f"quests.{category} : categorie invalide, attendu snake_case "
                    f"sans tiret ni accent",
                )
            if not isinstance(value, int) or isinstance(value, bool):
                report.error(meta, f"quests.{category} : '{value}' n'est pas un entier")
            elif value < 0:
                report.error(meta, f"quests.{category} : {value} est negatif")

    if progress.playtime_minutes is not None and progress.playtime_precision is None:
        report.error(
            meta,
            "playtime_precision est requis des que playtime_minutes est renseigne "
            "(sinon un total de carriere laisserait croire a une exactitude "
            "a la minute qui n'existe pas)",
        )
    if progress.playtime_precision is not None and progress.playtime_precision not in PRECISIONS:
        report.error(
            meta,
            f"playtime_precision '{progress.playtime_precision}' invalide, "
            f"attendu {' | '.join(PRECISIONS)}",
        )

    for index, source in enumerate(data.sources, start=1):
        label = f"sources[{index}]"
        if source.kind not in SOURCE_KINDS:
            report.error(
                meta,
                f"{label} : kind '{source.kind}' invalide, "
                f"attendu {' | '.join(SOURCE_KINDS)}",
            )
        _check_day(source.captured_on, meta, f"{label} : captured_on", report)
        if source.image is not None and not (root / source.image).exists():
            report.error(meta, f"{label} : image introuvable ({source.image})")

    if data.has_progress and not data.sources:
        report.error(
            meta,
            "au moins un bloc [[sources]] est requis des qu'une valeur de "
            "[progress] est renseignee : un chiffre sans source n'est pas verifiable",
        )

    hunts_path = f"{game_dir}/hunts.csv"
    seen: dict[str, int] = {}
    for hunt in data.hunts:
        _check_reference_key(hunt.monster_id, ref.monsters, hunts_path,
                             "monster_id", report, hunt.line)
        if hunt.monster_id in seen:
            report.error(
                hunts_path,
                f"monster_id '{hunt.monster_id}' deja present ligne "
                f"{seen[hunt.monster_id]}",
                hunt.line,
            )
        else:
            seen[hunt.monster_id] = hunt.line
        _check_counter(hunt.hunted, hunts_path, "hunted", hunt.line, report)
        _check_counter(hunt.captured, hunts_path, "captured", hunt.line, report)
        if (
            hunt.hunted is not None
            and hunt.captured is not None
            and hunt.captured > hunt.hunted
        ):
            report.error(
                hunts_path,
                f"captured ({hunt.captured}) superieur a hunted ({hunt.hunted})",
                hunt.line,
            )

    weapons_path = f"{game_dir}/weapons.csv"
    seen_weapons: dict[str, int] = {}
    for use in data.weapon_uses:
        _check_reference_key(use.weapon_id, ref.weapons, weapons_path,
                             "weapon_id", report, use.line)
        if use.weapon_id in seen_weapons:
            report.error(
                weapons_path,
                f"weapon_id '{use.weapon_id}' deja present ligne "
                f"{seen_weapons[use.weapon_id]}",
                use.line,
            )
        else:
            seen_weapons[use.weapon_id] = use.line
        _check_counter(use.uses, weapons_path, "uses", use.line, report)

    if not data.hunts:
        report.warn(game_dir, "aucune donnee de chasse")


def validate(
    ref: Reference, games: dict[str, GameData], root: Path, report: Report
) -> None:
    validate_reference(ref, root, report)

    for game_id, data in games.items():
        if game_id not in ref.games:
            report.error(
                f"data/games/{game_id}",
                f"dossier sans entree correspondante dans games.toml"
                f"{suggest(game_id, ref.games)}",
            )
            continue
        validate_game_data(data, ref, root, report)

    # Un jeu declare mais pas encore saisi est normal tant que la phase 3 dure :
    # c'est un avertissement, pas une erreur.
    for game_id in ref.games:
        if game_id not in games:
            report.warn(f"{REFERENCE_DIR}/games.toml",
                        f"jeu '{game_id}' declare mais aucun dossier data/games/{game_id}")

    hunted_ids = {hunt.monster_id for data in games.values() for hunt in data.hunts}
    for monster_id in ref.monsters:
        if monster_id not in hunted_ids:
            report.warn(f"{REFERENCE_DIR}/monsters.toml",
                        f"monstre '{monster_id}' reference par aucun jeu")
