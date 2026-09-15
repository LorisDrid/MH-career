"""Build de deploiement, execute par Cloudflare Pages.

L'hebergeur ne fournit pas Zola. Ce script le telecharge a version EPINGLEE,
verifie son empreinte, genere les donnees puis construit le site — le tout en
bibliotheque standard, comme le reste du projet.

    python3 -m tools.deploy

Rien ici n'est propre a Cloudflare hormis la lecture d'une variable
d'environnement : le script fonctionnerait tel quel chez un autre hebergeur.

Pourquoi en Python plutot qu'en commande shell chez l'hebergeur : la discipline
de version epinglee et de somme de controle etait le point le plus fragile du
deploiement. La mettre dans du code plutot que dans une chaine de
configuration la rend lisible, commentee et modifiable au meme endroit que le
reste de la chaine.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

from tools.build import run as build_data
from tools.loaders import repo_root

ZOLA_VERSION = "0.22.1"

# Empreinte relevee dans le journal du premier deploiement (2026-09-15). Toute
# modification ulterieure de l'archive fera desormais echouer le build.
# Si elle etait videe, le telechargement ne serait plus verifie mais un
# avertissement le signalerait : l'absence de controle reste visible.
ZOLA_SHA256 = "0ca09aa40376aaa9ddfb512ff9ad963262ef95edb0d0f2d5ec6961b6f5cf22ef"

ARCHIVE = f"zola-v{ZOLA_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
URL = f"https://github.com/getzola/zola/releases/download/v{ZOLA_VERSION}/{ARCHIVE}"


def unbuffer_output() -> None:
    """Force l'ecriture ligne par ligne.

    Hors terminal, Python bufferise sa sortie par blocs alors que les
    sous-processus ecrivent directement. Dans le journal du premier
    deploiement, les messages de Zola apparaissaient ainsi AVANT ceux qui
    annoncaient son telechargement. Le journal etant la seule surface de
    diagnostic d'un deploiement, son ordre doit etre fidele.
    """
    sys.stdout.reconfigure(line_buffering=True)


def check_python() -> None:
    """tomllib exige Python 3.11 : mieux vaut un message clair qu'un ImportError."""
    if sys.version_info < (3, 11):
        sys.exit(
            f"Python {sys.version_info.major}.{sys.version_info.minor} detecte, "
            f"3.11 minimum requis (tomllib est en stdlib depuis 3.11)."
        )


def fetch_zola(destination: Path) -> Path:
    """Telecharge, verifie et extrait le binaire Zola. Renvoie son chemin."""
    print(f"Telechargement de Zola {ZOLA_VERSION}")
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / ARCHIVE
        with urllib.request.urlopen(URL, timeout=120) as response:
            archive.write_bytes(response.read())

        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        print(f"SHA-256 de l'archive : {digest}")
        if ZOLA_SHA256:
            if digest != ZOLA_SHA256:
                sys.exit(
                    "Empreinte inattendue : l'archive telechargee ne correspond "
                    f"pas a la valeur epinglee.\n  attendu : {ZOLA_SHA256}\n"
                    f"  obtenu  : {digest}"
                )
            print("Empreinte conforme a la valeur epinglee.")
        else:
            print(
                "AVERTISSEMENT : aucune empreinte epinglee, telechargement non "
                "verifie. Reporter la valeur ci-dessus dans ZOLA_SHA256."
            )

        destination.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive) as tar:
            # filter="data" refuse les chemins absolus et les liens sortants.
            tar.extract("zola", path=destination, filter="data")

    binary = destination / "zola"
    binary.chmod(0o755)
    return binary


def site_base_url() -> str | None:
    """URL du site, lue dans l'environnement de construction.

    Une seule source : SITE_BASE_URL, surcharge explicite que l'on renseigne
    chez l'hebergeur. Absente, Zola retombe sur config.toml.

    CF_PAGES_URL a ete essayee puis RETIREE : Cloudflare la renseigne de
    maniere intermittente, et elle designe le deploiement COURANT. Le site
    deploye le 2026-09-15 s'est ainsi retrouve avec tous ses liens absolus
    pointant vers 775015a0.mh-career.pages.dev au lieu de son adresse
    canonique. Une valeur versionnee dans config.toml vaut mieux qu'une
    variable d'environnement au contenu changeant.
    """
    value = os.environ.get("SITE_BASE_URL")
    return value.rstrip("/") if value else None


def main() -> int:
    unbuffer_output()
    check_python()
    root = repo_root()

    zola = fetch_zola(root / "bin")
    print(subprocess.run([str(zola), "--version"], check=True,
                         capture_output=True, text=True).stdout.strip())

    print("\nGeneration des donnees")
    code = build_data(root)
    if code != 0:
        return code

    command = [str(zola), "build"]
    base_url = site_base_url()
    if base_url:
        command += ["--base-url", base_url]
        print(f"\nConstruction du site pour {base_url}")
    else:
        print("\nConstruction du site (base_url du fichier de configuration)")
    return subprocess.run(command, cwd=root).returncode


if __name__ == "__main__":
    raise SystemExit(main())
