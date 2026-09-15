"""Point d'entree du pipeline de donnees.

    python -m tools.build            valide, agrege, ecrit data/generated/site.json
    python -m tools.build --check    validation seule, code de sortie non nul si erreur

Lance en module (-m) et non en script : `python tools/build.py` placerait
tools/ sur le sys.path au lieu de la racine, et les imports internes
echoueraient.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.aggregate import build_site
from tools.exports import write_all
from tools.loaders import load_all_game_data, load_reference, repo_root
from tools.report import Report
from tools.validate import validate

OUTPUT = Path("data") / "generated" / "site.json"


def run(root: Path, *, check_only: bool = False, stream=sys.stdout) -> int:
    report = Report()
    ref = load_reference(root, report)
    games = load_all_game_data(root, report)
    validate(ref, games, root, report)

    rendered = report.render()
    if rendered:
        print(rendered, file=stream)

    if not report.ok:
        print(f"\nBuild interrompu : {len(report.errors)} erreur(s).", file=stream)
        return 1

    if check_only:
        print("Validation OK.", file=stream)
        return 0

    site = build_site(ref, games)
    destination = root / OUTPUT
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(site, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    exported = write_all(root, ref, games)

    totals = site["totals"]
    flat = ", ".join(f"{name} ({rows} lignes)" for name, rows in exported.items())
    print(
        f"\nEcrit {OUTPUT.as_posix()} : "
        f"{totals['games']} jeu(x) declare(s), "
        f"{totals['games_with_data']} avec donnees, "
        f"{len(site['bestiary'])} monstre(s) au bestiaire.\n"
        f"Exports plats : {flat}",
        file=stream,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m tools.build",
        description="Valide les sources et genere data/generated/site.json.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="valider sans rien ecrire (code de sortie non nul si erreur)",
    )
    parser.add_argument(
        "--root", type=Path, default=None,
        help="racine du depot (par defaut : celle deduite du fichier)",
    )
    args = parser.parse_args(argv)
    return run(args.root or repo_root(), check_only=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
