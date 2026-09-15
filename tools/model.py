"""Entites du domaine.

Regle transversale (AGENTS.md 2.3) : un compteur vaut int | None.
  None -> inconnu, non releve, non affiche par le jeu
  0    -> zero CONSTATE

Les deux ne doivent jamais etre confondus, ni a la lecture, ni a l'agregation,
ni au rendu.
"""
from __future__ import annotations

from dataclasses import dataclass, field

WEAPON_IDS = (
    "great_sword",
    "long_sword",
    "sword_and_shield",
    "dual_blades",
    "hammer",
    "hunting_horn",
    "lance",
    "gunlance",
    "switch_axe",
    "charge_blade",
    "insect_glaive",
    "light_bowgun",
    "heavy_bowgun",
    "bow",
)

PRECISIONS = ("minutes", "hours")
GAME_STATUSES = ("finished", "ongoing", "planned")
VARIANT_TYPES = ("subspecies", "rare_species", "deviant", "apex", "variant")
SOURCE_KINDS = ("guild_card", "hunter_notes", "hunting_log", "platform_stats", "api")


@dataclass(frozen=True)
class Platform:
    id: str
    name: str
    manufacturer: str | None = None
    released: int | None = None


@dataclass(frozen=True)
class Game:
    id: str
    title: str
    short_title: str
    platform: str
    generation: int | None = None
    released: int | None = None
    played_from: str | None = None
    played_to: str | None = None
    status: str = "planned"


@dataclass(frozen=True)
class Species:
    id: str
    name_en: str
    name_fr: str


@dataclass(frozen=True)
class Monster:
    id: str
    name_en: str
    name_fr: str
    species: str
    debut: str | None = None
    base: str | None = None
    variant_type: str | None = None

    @property
    def is_variant(self) -> bool:
        return self.base is not None


@dataclass(frozen=True)
class Weapon:
    id: str
    name_en: str
    name_fr: str | None = None
    category: str | None = None
    introduced: str | None = None


@dataclass(frozen=True)
class Source:
    kind: str
    captured_on: str
    image: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class Hunt:
    """Une ligne de hunts.csv. `line` sert aux messages d'erreur."""

    monster_id: str
    hunted: int | None
    captured: int | None
    notes: str | None
    line: int


@dataclass(frozen=True)
class WeaponUse:
    weapon_id: str
    uses: int | None
    notes: str | None
    line: int


@dataclass
class Progress:
    """Tout est optionnel : on n'ecrit que ce que le jeu affiche reellement."""

    hunter_rank: int | None = None
    master_rank: int | None = None
    village_rank: int | None = None
    playtime_minutes: int | None = None
    playtime_precision: str | None = None
    quests_completed: int | None = None
    quests_failed: int | None = None
    primary_weapon: str | None = None
    hunter_name: str | None = None


@dataclass
class GameData:
    game_id: str
    progress: Progress = field(default_factory=Progress)
    sources: list[Source] = field(default_factory=list)
    hunts: list[Hunt] = field(default_factory=list)
    weapon_uses: list[WeaponUse] = field(default_factory=list)

    @property
    def has_progress(self) -> bool:
        return any(v is not None for v in vars(self.progress).values())


@dataclass
class Reference:
    platforms: dict[str, Platform] = field(default_factory=dict)
    games: dict[str, Game] = field(default_factory=dict)
    species: dict[str, Species] = field(default_factory=dict)
    monsters: dict[str, Monster] = field(default_factory=dict)
    weapons: dict[str, Weapon] = field(default_factory=dict)
