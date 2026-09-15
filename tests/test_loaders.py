"""Tests des chargeurs TOML et CSV."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.loaders import load_all_game_data, load_game_data, load_reference
from tools.report import Report

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class ReferenceLoadingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.report = Report()
        self.ref = load_reference(FIXTURES, self.report)

    def test_fixture_reference_has_no_error(self) -> None:
        self.assertEqual([p.render() for p in self.report.errors], [])

    def test_entities_are_indexed_by_id(self) -> None:
        self.assertEqual(len(self.ref.monsters), 3)
        self.assertEqual(self.ref.games["test_game_x"].short_title, "TGX")

    def test_variant_links_to_its_base_form(self) -> None:
        variant = self.ref.monsters["test_monster_a_variant"]
        self.assertTrue(variant.is_variant)
        self.assertEqual(variant.base, "test_monster_a")
        self.assertFalse(self.ref.monsters["test_monster_a"].is_variant)

    def test_absent_optional_field_stays_none(self) -> None:
        # name_fr n'est pas renseigne dans la fixture d'armes : il doit rester
        # None, surtout pas une chaine vide qui ressemblerait a une saisie.
        self.assertIsNone(self.ref.weapons["great_sword"].name_fr)


class GameDataLoadingTest(unittest.TestCase):
    def setUp(self) -> None:
        self.report = Report()
        self.data = load_game_data(FIXTURES, "test_game_x", self.report)
        self.hunts = {h.monster_id: h for h in self.data.hunts}

    def test_fixture_game_has_no_error(self) -> None:
        self.assertEqual([p.render() for p in self.report.errors], [])

    def test_empty_cell_is_unknown_not_zero(self) -> None:
        """La distinction qui fonde tout le modele de donnees."""
        self.assertIsNone(self.hunts["test_monster_a_variant"].captured)

    def test_explicit_zero_is_preserved(self) -> None:
        self.assertEqual(self.hunts["test_monster_b"].hunted, 0)
        self.assertEqual(self.hunts["test_monster_b"].captured, 0)

    def test_line_numbers_are_recorded(self) -> None:
        # L'en-tete occupe la ligne 1 : la premiere donnee est en ligne 2.
        self.assertEqual(self.hunts["test_monster_a"].line, 2)
        self.assertEqual(self.hunts["test_monster_b"].line, 4)

    def test_notes_are_read_and_stripped(self) -> None:
        self.assertIsNone(self.hunts["test_monster_a"].notes)
        self.assertIn("capture", self.hunts["test_monster_a_variant"].notes)

    def test_progress_and_sources_are_loaded(self) -> None:
        self.assertEqual(self.data.progress.hunter_rank, 7)
        self.assertEqual(self.data.progress.quests_completed, 0)
        self.assertEqual(len(self.data.sources), 1)
        self.assertTrue(self.data.has_progress)

    def test_weapon_use_without_counter_is_unknown(self) -> None:
        uses = {u.weapon_id: u.uses for u in self.data.weapon_uses}
        self.assertEqual(uses["great_sword"], 12)
        self.assertIsNone(uses["long_sword"])

    def test_discovery_finds_the_fixture_game(self) -> None:
        self.assertEqual(list(load_all_game_data(FIXTURES, Report())), ["test_game_x"])


class MalformedInputTest(unittest.TestCase):
    """Un fichier mal forme doit produire un message localise, pas une exception."""

    def _load_hunts(self, csv_text: str) -> Report:
        report = Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            game_dir = root / "data" / "games" / "test_game_x"
            game_dir.mkdir(parents=True)
            (game_dir / "hunts.csv").write_text(csv_text, encoding="utf-8")
            load_game_data(root, "test_game_x", report)
        return report

    def test_non_integer_counter_is_reported_with_line(self) -> None:
        report = self._load_hunts(
            "monster_id,hunted\ntest_monster_a,beaucoup\n"
        )
        self.assertEqual(len(report.errors), 1)
        message = report.errors[0].render()
        self.assertIn("hunts.csv:2", message)
        self.assertIn("beaucoup", message)

    def test_unknown_column_is_reported(self) -> None:
        report = self._load_hunts("monster_id,hunted,hunted_typo\ntest_monster_a,1,2\n")
        self.assertTrue(
            any("hunted_typo" in p.render() for p in report.errors),
            "une colonne inconnue doit etre signalee, pas ignoree en silence",
        )

    def test_missing_key_column_is_reported(self) -> None:
        report = self._load_hunts("hunted,captured\n1,2\n")
        self.assertTrue(any("monster_id" in p.render() for p in report.errors))

    def test_unreadable_toml_is_reported_not_raised(self) -> None:
        report = Report()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data" / "reference").mkdir(parents=True)
            (root / "data" / "reference" / "monsters.toml").write_text(
                "[monsters\nbroken", encoding="utf-8"
            )
            load_reference(root, report)
        self.assertTrue(any("TOML illisible" in p.render() for p in report.errors))


if __name__ == "__main__":
    unittest.main()
