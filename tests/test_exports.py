"""Tests des exports plats."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from tools.exports import write_all
from tools.loaders import load_all_game_data, load_reference
from tools.report import Report

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def export_rows():
    ref = load_reference(FIXTURES, Report())
    games = load_all_game_data(FIXTURES, Report())
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_all(root, ref, games)
        base = root / "data" / "generated"
        with (base / "hunts-all.csv").open(encoding="utf-8-sig", newline="") as fh:
            hunts = list(csv.DictReader(fh))
        with (base / "weapons-all.csv").open(encoding="utf-8-sig", newline="") as fh:
            weapons = list(csv.DictReader(fh))
    return hunts, weapons


class FlatExportTest(unittest.TestCase):
    def setUp(self) -> None:
        self.hunts, self.weapons = export_rows()
        self.by_monster = {row["monster_id"]: row for row in self.hunts}

    def test_every_hunt_row_carries_its_game(self) -> None:
        """Le format long : le jeu est une colonne, pas un fichier."""
        self.assertTrue(all(row["game"] == "test_game_x" for row in self.hunts))
        self.assertEqual(len(self.hunts), 3)

    def test_unknown_stays_an_empty_cell(self) -> None:
        """La distinction inconnu / zero doit survivre a l'export."""
        self.assertEqual(self.by_monster["test_monster_a_variant"]["captured"], "")

    def test_confirmed_zero_stays_a_zero(self) -> None:
        self.assertEqual(self.by_monster["test_monster_b"]["hunted"], "0")
        self.assertEqual(self.by_monster["test_monster_b"]["captured"], "0")

    def test_variant_resolves_to_its_base_form(self) -> None:
        # C'est cette colonne qui rend le tableur capable de regrouper
        # les variantes sans connaitre le referentiel.
        row = self.by_monster["test_monster_a_variant"]
        self.assertEqual(row["base_form"], "test_monster_a")
        self.assertEqual(row["variant_type"], "subspecies")

    def test_base_form_of_a_non_variant_is_itself(self) -> None:
        self.assertEqual(self.by_monster["test_monster_a"]["base_form"], "test_monster_a")

    def test_weapon_export_preserves_unknown(self) -> None:
        by_weapon = {row["weapon_id"]: row for row in self.weapons}
        self.assertEqual(by_weapon["great_sword"]["uses"], "12")
        self.assertEqual(by_weapon["long_sword"]["uses"], "")


if __name__ == "__main__":
    unittest.main()
