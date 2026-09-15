"""Tests des controles d'integrite.

Chaque test verifie qu'une donnee invalide est bien REFUSEE. Un validateur dont
on n'a jamais observe l'echec ne prouve rien.
"""
from __future__ import annotations

import dataclasses
import unittest
from datetime import date, timedelta
from pathlib import Path

from tools.loaders import load_all_game_data, load_reference
from tools.model import GameData, Hunt, Monster, Source, WeaponUse
from tools.report import Report
from tools.validate import validate

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def base_reference():
    return load_reference(FIXTURES, Report())


def base_games():
    return load_all_game_data(FIXTURES, Report())


def errors_for(ref, games) -> list[str]:
    report = Report()
    validate(ref, games, FIXTURES, report)
    return [p.render() for p in report.errors]


def assert_mentions(testcase, messages, *fragments) -> None:
    joined = "\n".join(messages)
    for fragment in fragments:
        testcase.assertIn(fragment, joined)


class ValidFixtureTest(unittest.TestCase):
    def test_fixture_universe_is_valid(self) -> None:
        self.assertEqual(errors_for(base_reference(), base_games()), [])


class IdentifierTest(unittest.TestCase):
    def test_hyphen_in_identifier_is_rejected(self) -> None:
        """Un tiret casserait Tera : monsters.a-b y est une soustraction."""
        ref = base_reference()
        ref.monsters["test-monster-c"] = Monster(
            id="test-monster-c", name_en="C", name_fr="C", species="test_species"
        )
        assert_mentions(self, errors_for(ref, base_games()),
                        "test-monster-c", "snake_case")

    def test_accented_identifier_is_rejected(self) -> None:
        ref = base_reference()
        ref.species["espece_speciale"] = dataclasses.replace(
            ref.species["test_species"], id="Espece"
        )
        ref.species["Espece"] = ref.species.pop("espece_speciale")
        assert_mentions(self, errors_for(ref, base_games()), "identifiant invalide")


class ReferentialIntegrityTest(unittest.TestCase):
    def test_unknown_monster_id_is_reported_with_a_suggestion(self) -> None:
        games = base_games()
        games["test_game_x"].hunts.append(
            Hunt(monster_id="test_monster_aa", hunted=1, captured=None, notes=None, line=9)
        )
        assert_mentions(self, errors_for(base_reference(), games),
                        "hunts.csv:9", "test_monster_aa", "voulais-tu 'test_monster_a'")

    def test_unknown_weapon_id_is_reported(self) -> None:
        games = base_games()
        games["test_game_x"].weapon_uses.append(
            WeaponUse(weapon_id="grate_sword", uses=3, notes=None, line=5)
        )
        assert_mentions(self, errors_for(base_reference(), games),
                        "grate_sword", "voulais-tu 'great_sword'")

    def test_variant_pointing_to_a_variant_is_rejected(self) -> None:
        ref = base_reference()
        ref.monsters["test_monster_b"] = dataclasses.replace(
            ref.monsters["test_monster_b"],
            base="test_monster_a_variant",
            variant_type="subspecies",
        )
        assert_mentions(self, errors_for(ref, base_games()),
                        "elle-meme une variante")

    def test_base_without_variant_type_is_rejected(self) -> None:
        ref = base_reference()
        ref.monsters["test_monster_b"] = dataclasses.replace(
            ref.monsters["test_monster_b"], base="test_monster_a"
        )
        assert_mentions(self, errors_for(ref, base_games()),
                        "base et variant_type")

    def test_game_directory_without_reference_entry_is_rejected(self) -> None:
        games = base_games()
        games["test_game_y"] = GameData(game_id="test_game_y")
        assert_mentions(self, errors_for(base_reference(), games),
                        "test_game_y", "games.toml")


class CounterConsistencyTest(unittest.TestCase):
    def test_captured_greater_than_hunted_is_rejected(self) -> None:
        games = base_games()
        games["test_game_x"].hunts = [
            Hunt(monster_id="test_monster_a", hunted=2, captured=5, notes=None, line=2)
        ]
        assert_mentions(self, errors_for(base_reference(), games),
                        "captured (5)", "hunted (2)")

    def test_negative_counter_is_rejected(self) -> None:
        games = base_games()
        games["test_game_x"].hunts = [
            Hunt(monster_id="test_monster_a", hunted=-3, captured=None, notes=None, line=2)
        ]
        assert_mentions(self, errors_for(base_reference(), games), "negatif")

    def test_duplicate_monster_id_is_rejected(self) -> None:
        games = base_games()
        games["test_game_x"].hunts.append(
            Hunt(monster_id="test_monster_a", hunted=1, captured=None, notes=None, line=7)
        )
        assert_mentions(self, errors_for(base_reference(), games),
                        "deja present ligne 2")

    def test_unknown_counter_never_triggers_a_comparison(self) -> None:
        """captured inconnu ne doit pas etre compare a hunted comme s'il valait 0."""
        games = base_games()
        games["test_game_x"].hunts = [
            Hunt(monster_id="test_monster_a", hunted=0, captured=None, notes=None, line=2)
        ]
        self.assertEqual(errors_for(base_reference(), games), [])


class ProgressTest(unittest.TestCase):
    def test_playtime_without_precision_is_rejected(self) -> None:
        games = base_games()
        games["test_game_x"].progress.playtime_precision = None
        assert_mentions(self, errors_for(base_reference(), games),
                        "playtime_precision est requis")

    def test_invalid_precision_value_is_rejected(self) -> None:
        games = base_games()
        games["test_game_x"].progress.playtime_precision = "secondes"
        assert_mentions(self, errors_for(base_reference(), games), "secondes")

    def test_progress_without_source_is_rejected(self) -> None:
        """Un chiffre sans source n'est pas verifiable, donc pas archivable."""
        games = base_games()
        games["test_game_x"].sources = []
        assert_mentions(self, errors_for(base_reference(), games), "[[sources]]")

    def test_future_capture_date_is_rejected(self) -> None:
        games = base_games()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        games["test_game_x"].sources = [Source(kind="guild_card", captured_on=tomorrow)]
        assert_mentions(self, errors_for(base_reference(), games), "dans le futur")

    def test_missing_source_image_is_rejected(self) -> None:
        games = base_games()
        games["test_game_x"].sources = [
            Source(kind="guild_card", captured_on="2020-06-15",
                   image="static/sources/absente.jpg")
        ]
        assert_mentions(self, errors_for(base_reference(), games), "image introuvable")


class GamePeriodTest(unittest.TestCase):
    def test_played_from_after_played_to_is_rejected(self) -> None:
        ref = base_reference()
        ref.games["test_game_x"] = dataclasses.replace(
            ref.games["test_game_x"], played_from="2021-01", played_to="2020-06"
        )
        assert_mentions(self, errors_for(ref, base_games()), "posterieur")

    def test_malformed_month_is_rejected(self) -> None:
        ref = base_reference()
        ref.games["test_game_x"] = dataclasses.replace(
            ref.games["test_game_x"], played_from="janvier 2020"
        )
        assert_mentions(self, errors_for(ref, base_games()), "YYYY-MM")

    def test_invalid_status_is_rejected(self) -> None:
        ref = base_reference()
        ref.games["test_game_x"] = dataclasses.replace(
            ref.games["test_game_x"], status="abandonne"
        )
        assert_mentions(self, errors_for(ref, base_games()), "abandonne")


if __name__ == "__main__":
    unittest.main()
