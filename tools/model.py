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
    # Pas un type d'arme de la licence, mais Generations le compte dans sa page
    # "Utilisation des armes" : l'exclure perdrait une donnee affichee.
    "prowler",
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
    """L'espece est OPTIONNELLE : aucune Guild Card ne l'affiche, donc l'exiger
    obligerait a la tirer d'une source externe au jeu. On la renseigne quand on
    l'a verifiee, jamais par defaut."""

    id: str
    name_en: str
    name_fr: str
    species: str | None = None
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
    """Tout est optionnel : on n'ecrit que ce que le jeu affiche reellement.

    `quests` est une table categorie -> nombre, et non un total unique : les
    jeux ventilent leurs quetes differemment (MH4U distingue caravane, grande
    salle, rang G, arene...). Stocker le detail affiche plutot qu'une somme
    evite d'ecrire un nombre qui n'apparait sur aucun ecran. Le total est
    calcule a l'agregation.

    Un jeu qui n'afficherait qu'un total s'ecrit quests = { total = 148 }.
    """

    hunter_rank: int | None = None
    master_rank: int | None = None
    village_rank: int | None = None
    playtime_minutes: int | None = None
    playtime_precision: str | None = None
    quests: dict[str, int] = field(default_factory=dict)
    primary_weapon: str | None = None
    hunter_name: str | None = None
    title: str | None = None


@dataclass
class GameData:
    game_id: str
    progress: Progress = field(default_factory=Progress)
    sources: list[Source] = field(default_factory=list)
    hunts: list[Hunt] = field(default_factory=list)
    weapon_uses: list[WeaponUse] = field(default_factory=list)

    @property
    def has_progress(self) -> bool:
        # Un dict vide vaut absence ; 0 reste une valeur presente (zero constate).
        return any(
            bool(value) if isinstance(value, dict) else value is not None
            for value in vars(self.progress).values()
        )


@dataclass
class Reference:
    platforms: dict[str, Platform] = field(default_factory=dict)
    games: dict[str, Game] = field(default_factory=dict)
    species: dict[str, Species] = field(default_factory=dict)
    monsters: dict[str, Monster] = field(default_factory=dict)
    weapons: dict[str, Weapon] = field(default_factory=dict)
