"""Lecture des sources TOML et CSV.

Les chargeurs sont TOLERANTS : ils signalent les problemes au rapport et
poursuivent, pour que l'utilisateur voie toutes ses erreurs de saisie d'un coup.
Seul un fichier syntaxiquement illisible interrompt son propre chargement.

Ils conservent les numeros de ligne des CSV : sur un fichier de 200 monstres,
une erreur sans numero de ligne est inutilisable.
"""
from __future__ import annotations

import csv
import tomllib
from pathlib import Path

from tools.model import (
    Game,
    GameData,
    Hunt,
    Monster,
    Platform,
    Progress,
    Reference,
    Source,
    Species,
    Weapon,
    WeaponUse,
)
from tools.report import Report


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def rel(path: Path, root: Path) -> str:
    """Chemin relatif au repo, en separateurs POSIX, pour les messages."""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def read_toml(path: Path, root: Path, report: Report) -> dict | None:
    if not path.exists():
        report.error(rel(path, root), "fichier introuvable")
        return None
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except tomllib.TOMLDecodeError as exc:
        report.error(rel(path, root), f"TOML illisible : {exc}")
        return None


def _fields(
    raw: dict,
    entity_id: str,
    where: str,
    report: Report,
    *,
    required: tuple[str, ...],
    allowed: tuple[str, ...],
) -> dict | None:
    """Verifie les cles d'une entite et renvoie un dict propre.

    Refuser les cles inconnues n'est pas du zele : une faute de frappe sur un
    nom de champ (name_fre au lieu de name_fr) serait sinon ignoree en silence,
    et la valeur saisie perdue sans que rien ne le signale.
    """
    if not isinstance(raw, dict):
        report.error(where, f"'{entity_id}' devrait etre une table TOML")
        return None
    out: dict = {}
    for key in required:
        if key not in raw:
            report.error(where, f"'{entity_id}' : champ requis '{key}' absent")
        else:
            out[key] = raw[key]
    for key in allowed:
        if key in raw:
            out[key] = raw[key]
    unknown = set(raw) - set(required) - set(allowed)
    for key in sorted(unknown):
        report.error(where, f"'{entity_id}' : champ inconnu '{key}'")
    return out if all(k in out for k in required) else None


#: (fichier, table TOML, classe, champs requis, champs optionnels, attribut de Reference)
_REFERENCE_SPECS = (
    ("platforms.toml", "platforms", Platform,
     ("name",), ("manufacturer", "released"), "platforms"),
    ("games.toml", "games", Game,
     ("title", "short_title", "platform"),
     ("generation", "released", "played_from", "played_to", "status"), "games"),
    ("species.toml", "species", Species,
     ("name_en", "name_fr"), (), "species"),
    ("monsters.toml", "monsters", Monster,
     ("name_en", "name_fr"), ("species", "debut", "base", "variant_type"), "monsters"),
    ("weapons.toml", "weapons", Weapon,
     ("name_en",), ("name_fr", "category", "introduced"), "weapons"),
)


def load_reference(root: Path, report: Report) -> Reference:
    ref = Reference()
    base = root / "data" / "reference"

    for filename, table, factory, required, allowed, attr in _REFERENCE_SPECS:
        path = base / filename
        where = rel(path, root)
        raw = read_toml(path, root, report)
        if raw is None:
            continue
        entities = raw.get(table)
        if entities is None:
            report.error(where, f"table '[{table}]' absente")
            continue
        target: dict = getattr(ref, attr)
        for entity_id, body in entities.items():
            fields = _fields(body, entity_id, where, report,
                             required=required, allowed=allowed)
            if fields is None:
                continue
            try:
                target[entity_id] = factory(id=entity_id, **fields)
            except TypeError as exc:
                report.error(where, f"'{entity_id}' : {exc}")
    return ref


def discover_game_dirs(root: Path) -> list[str]:
    games_dir = root / "data" / "games"
    if not games_dir.is_dir():
        return []
    return sorted(p.name for p in games_dir.iterdir() if p.is_dir())


def _int_or_none(
    raw: str | None, where: str, line: int, column: str, report: Report
) -> int | None:
    """Cellule vide -> None (inconnu). Une valeur illisible est une erreur."""
    if raw is None:
        return None
    text = raw.strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        report.error(where, f"{column} : '{text}' n'est pas un entier", line)
        return None


def _text_or_none(raw: str | None) -> str | None:
    if raw is None:
        return None
    text = raw.strip()
    return text or None


def _read_counter_csv(
    path: Path,
    root: Path,
    report: Report,
    *,
    key_column: str,
    value_columns: tuple[str, ...],
) -> list[dict]:
    """Lit un CSV de compteurs, en annotant chaque ligne de son numero."""
    where = rel(path, root)
    rows: list[dict] = []
    if not path.exists():
        return rows
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            report.error(where, "fichier CSV vide (en-tete absente)")
            return rows
        if key_column not in reader.fieldnames:
            report.error(where, f"colonne requise absente : '{key_column}'")
            return rows
        unknown = set(reader.fieldnames) - {key_column, "notes"} - set(value_columns)
        for column in sorted(unknown):
            report.error(where, f"colonne inconnue : '{column}'")
        for raw in reader:
            line = reader.line_num
            key = _text_or_none(raw.get(key_column))
            if key is None:
                report.error(where, f"{key_column} vide", line)
                continue
            entry: dict = {
                key_column: key,
                "line": line,
                "notes": _text_or_none(raw.get("notes")),
            }
            for column in value_columns:
                entry[column] = _int_or_none(raw.get(column), where, line, column, report)
            rows.append(entry)
    return rows


def load_game_data(root: Path, game_id: str, report: Report) -> GameData:
    game_dir = root / "data" / "games" / game_id
    data = GameData(game_id=game_id)

    meta_path = game_dir / "meta.toml"
    if meta_path.exists():
        where = rel(meta_path, root)
        raw = read_toml(meta_path, root, report) or {}
        declared = raw.get("game")
        if declared is not None and declared != game_id:
            report.error(
                where, f"game = '{declared}' ne correspond pas au dossier '{game_id}'"
            )
        fields = _fields(
            raw.get("progress", {}), "progress", where, report,
            required=(), allowed=tuple(vars(Progress()).keys()),
        )
        if fields is not None:
            data.progress = Progress(**fields)
        for index, source_raw in enumerate(raw.get("sources", []), start=1):
            source_fields = _fields(
                source_raw, f"sources[{index}]", where, report,
                required=("kind", "captured_on"), allowed=("image", "note"),
            )
            if source_fields is not None:
                data.sources.append(Source(**source_fields))
        for key in sorted(set(raw) - {"game", "progress", "sources"}):
            report.error(where, f"cle inconnue a la racine : '{key}'")

    for row in _read_counter_csv(
        game_dir / "hunts.csv", root, report,
        key_column="monster_id", value_columns=("hunted", "captured"),
    ):
        data.hunts.append(
            Hunt(
                monster_id=row["monster_id"],
                hunted=row["hunted"],
                captured=row["captured"],
                notes=row["notes"],
                line=row["line"],
            )
        )

    for row in _read_counter_csv(
        game_dir / "weapons.csv", root, report,
        key_column="weapon_id", value_columns=("uses",),
    ):
        data.weapon_uses.append(
            WeaponUse(
                weapon_id=row["weapon_id"],
                uses=row["uses"],
                notes=row["notes"],
                line=row["line"],
            )
        )

    return data


def load_all_game_data(root: Path, report: Report) -> dict[str, GameData]:
    return {gid: load_game_data(root, gid, report) for gid in discover_game_dirs(root)}
