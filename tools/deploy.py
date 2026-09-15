"""Build de deploiement, execute par Vercel.

Vercel ne fournit pas Zola. Ce script le telecharge a version EPINGLEE, verifie
son empreinte, genere les donnees puis construit le site — le tout en
bibliotheque standard, comme le reste du projet.

    python3 -m tools.deploy

Pourquoi en Python plutot qu'en commande shell dans la configuration Vercel :
la discipline de version epinglee et de somme de controle etait le point le plus
fragile du deploiement. La mettre dans du code plutot que dans une chaine de
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

# Empreinte de l'archive, a renseigner apres le premier deploiement : elle est
# affichee dans le journal de build. Tant qu'elle est vide, le telechargement
# n'est pas verifie et un avertissement le signale — l'absence de controle
# reste ainsi visible au lieu d'etre silencieuse.
ZOLA_SHA256 = ""

ARCHIVE = f"zola-v{ZOLA_VERSION}-x86_64-unknown-linux-gnu.tar.gz"
URL = f"https://github.com/getzola/zola/releases/download/v{ZOLA_VERSION}/{ARCHIVE}"


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
    """URL de production, fournie par Vercel a la construction.

    La lire dans l'environnement plutot que de la figer dans config.toml evite
    de dependre du nom que Vercel attribuera au projet. En local, la variable
    est absente et Zola retombe sur la valeur du fichier de configuration.
    """
    host = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL")
    return f"https://{host}" if host else None


def main() -> int:
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
