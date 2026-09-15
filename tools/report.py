"""Collecte des problemes de validation.

Le rapport ACCUMULE les problemes au lieu de s'arreter au premier : corriger
200 lignes de CSV une par une, en relancant le build a chaque fois, serait
decourageant. Tout est affiche d'un coup, puis le build echoue.
"""
from __future__ import annotations

import difflib
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Problem:
    """Un probleme localise dans un fichier source."""

    path: str
    message: str
    line: int | None = None
    level: str = "error"

    def render(self) -> str:
        where = f"{self.path}:{self.line}" if self.line is not None else self.path
        return f"{where} - {self.message}"


@dataclass
class Report:
    problems: list[Problem] = field(default_factory=list)

    def error(self, path: str, message: str, line: int | None = None) -> None:
        self.problems.append(Problem(path, message, line, "error"))

    def warn(self, path: str, message: str, line: int | None = None) -> None:
        self.problems.append(Problem(path, message, line, "warning"))

    @property
    def errors(self) -> list[Problem]:
        return [p for p in self.problems if p.level == "error"]

    @property
    def warnings(self) -> list[Problem]:
        return [p for p in self.problems if p.level == "warning"]

    @property
    def ok(self) -> bool:
        """Vrai si rien ne bloque le build. Les avertissements ne bloquent pas."""
        return not self.errors

    def render(self) -> str:
        lines: list[str] = []
        if self.warnings:
            lines.append(f"{len(self.warnings)} avertissement(s) :")
            lines += [f"  ! {p.render()}" for p in self.warnings]
        if self.errors:
            if lines:
                lines.append("")
            lines.append(f"{len(self.errors)} erreur(s) :")
            lines += [f"  x {p.render()}" for p in self.errors]
        return "\n".join(lines)


def suggest(value: str, candidates) -> str:
    """Suffixe de suggestion pour une faute de frappe, ou chaine vide.

    La faute de frappe sur un identifiant est l'erreur la plus frequente lors de
    la saisie manuelle ; difflib la rattrape sans dependance externe.
    """
    matches = difflib.get_close_matches(value, list(candidates), n=1, cutoff=0.7)
    return f" (voulais-tu '{matches[0]}' ?)" if matches else ""
