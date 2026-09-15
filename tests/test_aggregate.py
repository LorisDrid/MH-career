"""Tests des calculs inter-jeux."""
from __future__ import annotations

import unittest
from pathlib import Path

from tools.aggregate import (
    build_bestiary,
    build_games,
    fraction,
    level_of,
    month_label,
    quantile_edges,
    build_site,
    build_timeline,
    build_totals,
    build_weapons,
    coarsest_precision,
    sum_or_none,
)
from tools.loaders import load_all_game_data, load_reference
from tools.model import Game, GameData, Hunt, Reference
from tools.report import Report

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def fixture_world():
    return load_reference(FIXTURES, Report()), load_all_game_data(FIXTURES, Report())


class SumOrNoneTest(unittest.TestCase):
    """Le test le plus important du projet.

    sum() renverrait 0 sur une liste entierement inconnue, affirmant "zero
    chasse" la ou la verite est "on ne sait pas". Sur une archive, cette
    confusion est une corruption de donnee.
    """

    def test_all_unknown_stays_unknown(self) -> None:
        self.assertIsNone(sum_or_none([None, None, None]))

    def test_empty_input_stays_unknown(self) -> None:
        self.assertIsNone(sum_or_none([]))

    def test_known_values_are_summed_ignoring_unknowns(self) -> None:
        self.assertEqual(sum_or_none([None, 3, None, 4]), 7)

    def test_confirmed_zero_is_not_unknown(self) -> None:
        self.assertEqual(sum_or_none([0]), 0)
        self.assertEqual(sum_or_none([0, None]), 0)


class PrecisionTest(unittest.TestCase):
    def test_coarsest_term_wins(self) -> None:
        # Un total ne peut pas etre plus precis que son terme le plus grossier.
        self.assertEqual(coarsest_precision(["minutes", "hours", "minutes"]), "hours")

    def test_all_precise_stays_precise(self) -> None:
        self.assertEqual(coarsest_precision(["minutes", "minutes"]), "minutes")

    def test_no_information_stays_unknown(self) -> None:
        self.assertIsNone(coarsest_precision([None, None]))
        self.assertIsNone(coarsest_precision([]))


class EmptyProjectTest(unittest.TestCase):
    """Etat de la phase 1 : des jeux declares, aucune donnee saisie."""

    def setUp(self) -> None:
        self.ref, _ = fixture_world()
        self.totals = build_totals(self.ref, {})

    def test_record_counts_are_real_zeros(self) -> None:
        # Denombrer 0 enregistrement est un fait vrai, pas une inconnue.
        self.assertEqual(self.totals["games_with_data"], 0)
        self.assertEqual(self.totals["monsters_recorded"], 0)

    def test_sums_of_unknown_values_stay_null(self) -> None:
        for key in ("playtime_minutes", "hunted", "captured", "quests_total"):
            with self.subTest(key=key):
                self.assertIsNone(self.totals[key])

    def test_bestiary_is_empty_not_fabricated(self) -> None:
        self.assertEqual(build_bestiary(self.ref, {}), [])


class TotalsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.ref, self.games = fixture_world()
        self.totals = build_totals(self.ref, self.games)

    def test_hunted_sums_every_form(self) -> None:
        self.assertEqual(self.totals["hunted"], 15)  # 10 + 5 + 0

    def test_captured_ignores_unknown_but_counts_zero(self) -> None:
        self.assertEqual(self.totals["captured"], 2)  # 2 + inconnu + 0

    def test_distinct_hunted_excludes_confirmed_zero(self) -> None:
        # 3 monstres enregistres, mais un seul a zero chasse constate.
        self.assertEqual(self.totals["monsters_recorded"], 3)
        self.assertEqual(self.totals["distinct_monsters_hunted"], 2)

    def test_career_span_is_derived_from_play_periods(self) -> None:
        self.assertEqual(self.totals["career_span"]["from"], "2020-01")
        self.assertEqual(self.totals["career_span"]["to"], "2020-06")


class BestiaryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.ref, self.games = fixture_world()
        self.bestiary = {row["id"]: row for row in build_bestiary(self.ref, self.games)}

    def test_variants_are_folded_into_their_base_form(self) -> None:
        group = self.bestiary["test_monster_a"]
        self.assertEqual(group["total_hunted"], 15)
        self.assertEqual({f["id"] for f in group["forms"]},
                         {"test_monster_a", "test_monster_a_variant"})

    def test_variant_is_not_listed_as_its_own_group(self) -> None:
        self.assertNotIn("test_monster_a_variant", self.bestiary)

    def test_detail_per_form_is_preserved(self) -> None:
        forms = {f["id"]: f["total_hunted"] for f in self.bestiary["test_monster_a"]["forms"]}
        self.assertEqual(forms["test_monster_a"], 10)
        self.assertEqual(forms["test_monster_a_variant"], 5)

    def test_ordering_puts_most_hunted_first(self) -> None:
        ordered = [row["id"] for row in build_bestiary(self.ref, self.games)]
        self.assertEqual(ordered, ["test_monster_a", "test_monster_b"])

    def test_group_of_entirely_unknown_counts_stays_unknown(self) -> None:
        games = {"test_game_x": GameData(
            game_id="test_game_x",
            hunts=[Hunt("test_monster_a", None, None, None, 2)],
        )}
        group = build_bestiary(self.ref, games)[0]
        self.assertIsNone(group["total_hunted"])


class WeaponsTest(unittest.TestCase):
    def test_usage_is_aggregated_and_unknown_preserved(self) -> None:
        ref, games = fixture_world()
        weapons = {row["id"]: row for row in build_weapons(ref, games)}
        self.assertEqual(weapons["great_sword"]["usage_score"], 12)
        self.assertIsNone(weapons["long_sword"]["usage_score"])


class VisualEncodingTest(unittest.TestCase):
    """Encodage visuel : la distinction inconnu / zero doit survivre au rendu."""

    def test_unknown_gets_no_bar(self) -> None:
        """None ne doit pas devenir 0 : pas de barre du tout, pas une barre vide."""
        self.assertIsNone(fraction(None, 100))

    def test_confirmed_zero_gets_an_empty_bar(self) -> None:
        # 0.0 et None se rendent pareil a l'ecran, mais seul 0.0 affirme un zero.
        self.assertEqual(fraction(0, 100), 0.0)

    def test_bar_is_linear(self) -> None:
        # Une longueur de barre doit rester proportionnelle a la valeur.
        self.assertEqual(fraction(50, 100), 0.5)
        self.assertEqual(fraction(100, 100), 1.0)

    def test_bar_survives_an_absent_maximum(self) -> None:
        self.assertIsNone(fraction(5, 0))
        self.assertIsNone(fraction(5, None))

    def test_unknown_and_zero_are_both_untinted(self) -> None:
        """La couleur ne porte que la magnitude ; le texte porte la distinction."""
        edges = [1, 4, 6, 10]
        self.assertIsNone(level_of(None, edges))
        self.assertIsNone(level_of(0, edges))

    def test_levels_climb_with_the_value(self) -> None:
        edges = [1, 4, 6, 10]
        self.assertEqual(level_of(1, edges), 0)
        self.assertEqual(level_of(2, edges), 1)
        self.assertEqual(level_of(5, edges), 2)
        self.assertEqual(level_of(7, edges), 3)
        self.assertEqual(level_of(999, edges), 4)

    def test_quantiles_spread_a_skewed_distribution(self) -> None:
        """Le decoupage lineaire echouerait ici : c'est tout l'interet."""
        values = [1] * 40 + [2, 3, 5, 8, 13, 21, 34, 55, 89, 123]
        edges = quantile_edges(values)
        self.assertTrue(edges, "des bornes doivent etre produites")
        levels = [level_of(v, edges) for v in values]
        # Aucun palier ne doit avaler la quasi-totalite des valeurs.
        for level in set(levels):
            share = levels.count(level) / len(levels)
            self.assertLess(share, 0.9, f"le palier {level} absorbe tout")

    def test_too_few_values_still_produce_usable_edges(self) -> None:
        self.assertEqual(quantile_edges([5]), [])
        self.assertEqual(quantile_edges([]), [])


class SiteDocumentTest(unittest.TestCase):
    def setUp(self) -> None:
        self.ref, self.games = fixture_world()
        self.site = build_site(self.ref, self.games)

    def test_games_are_also_indexed_by_id(self) -> None:
        self.assertEqual(
            {row["id"] for row in self.site["games"]},
            set(self.site["games_by_id"]),
        )

    def test_timeline_has_a_start_and_an_end(self) -> None:
        kinds = [event["kind"] for event in build_timeline(self.ref)]
        self.assertEqual(kinds, ["start", "end"])

    def test_schema_version_is_present(self) -> None:
        self.assertIn("schema_version", self.site["meta"])

    def test_empty_reference_produces_a_valid_document(self) -> None:
        site = build_site(Reference(), {})
        self.assertEqual(site["games"], [])
        self.assertIsNone(site["totals"]["hunted"])


class MonstersRecordedTest(unittest.TestCase):
    """Un bestiaire non relevé est inconnu, pas vide."""

    def test_a_game_without_hunts_reports_unknown(self):
        ref, games = fixture_world()
        rows = {row["id"]: row for row in build_games(ref, games)}
        empty = [row for row in rows.values() if not row["has_data"]]
        if not empty:
            self.skipTest("la fixture ne contient aucun jeu vide")
        for row in empty:
            self.assertIsNone(row["monsters_recorded"])

    def test_a_game_with_hunts_reports_a_count(self):
        ref, games = fixture_world()
        rows = [row for row in build_games(ref, games) if row["has_data"]]
        self.assertTrue(rows, "la fixture doit contenir au moins un jeu saisi")
        for row in rows:
            self.assertIsInstance(row["monsters_recorded"], int)
            self.assertGreater(row["monsters_recorded"], 0)


class MonthLabelTest(unittest.TestCase):
    """La date stockée est ISO ; la date affichée est française."""

    def test_converts_a_month(self):
        self.assertEqual(month_label("2016-07"), "juillet 2016")
        self.assertEqual(month_label("2025-01"), "janvier 2025")
        self.assertEqual(month_label("2018-12"), "décembre 2018")

    def test_unknown_stays_unknown(self):
        # Une date absente ne doit jamais devenir une chaîne affichable :
        # le template distingue None du reste pour afficher « — ».
        self.assertIsNone(month_label(None))
        self.assertIsNone(month_label(""))

    def test_unexpected_shape_passes_through(self):
        # Mieux vaut afficher la valeur brute que la déformer en silence.
        self.assertEqual(month_label("2016"), "2016")
        self.assertEqual(month_label("2016-13"), "2016-13")
        self.assertEqual(month_label("2016-07-18"), "2016-07-18")


class TimelineLabelTest(unittest.TestCase):
    def test_events_carry_a_readable_date_and_a_named_kind(self):
        # Construit à la main plutôt que lu depuis data/ : un test ne doit pas
        # dépendre de l'état de la saisie, qui change à chaque relevé.
        ref = Reference()
        ref.games["a"] = Game(id="a", title="Jeu A", short_title="A",
                              platform="p", played_from="2016-01",
                              played_to="2016-07")
        ref.games["b"] = Game(id="b", title="Jeu B", short_title="B",
                              platform="p")

        events = build_timeline(ref)

        self.assertEqual(len(events), 2)  # le jeu sans date n'en produit aucun
        self.assertEqual([e["kind"] for e in events], ["start", "end"])
        self.assertEqual([e["date"] for e in events], ["2016-01", "2016-07"])
        self.assertEqual([e["date_label"] for e in events],
                         ["janvier 2016", "juillet 2016"])
        self.assertEqual([e["kind_label"] for e in events],
                         ["première session", "dernière session"])


if __name__ == "__main__":
    unittest.main()
