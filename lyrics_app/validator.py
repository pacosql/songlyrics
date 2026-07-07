"""Validación cruzada de letras entre fuentes.

Se normalizan los textos y se comparan por pares con difflib.
Si dos o más fuentes coinciden por encima del umbral, la letra
se considera validada y se elige la versión más completa del
grupo mayoritario.
"""

from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.72


def normalize(text: str) -> str:
    """Normaliza para comparar: minúsculas, sin tildes ni puntuación,
    espacios colapsados. No se usa para el PDF, solo para comparar."""
    text = unicodedata.normalize("NFD", text.lower())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"\[.*?\]|\(.*?\)", " ", text)  # anotaciones tipo [Chorus]
    text = re.sub(r"[^a-z0-9ñ\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()


def validate(results: list[dict]) -> dict:
    """Devuelve un veredicto de validación.

    {
      "validated": bool,
      "chosen": dict | None,        # resultado elegido
      "agreeing_sources": [str],    # fuentes que coinciden entre sí
      "pairs": [(src_a, src_b, score)],
      "all_sources": [str],
    }
    """
    verdict = {
        "validated": False,
        "chosen": None,
        "agreeing_sources": [],
        "pairs": [],
        "all_sources": [r["source"] for r in results],
    }
    if not results:
        return verdict
    if len(results) == 1:
        verdict["chosen"] = results[0]
        verdict["agreeing_sources"] = [results[0]["source"]]
        return verdict

    n = len(results)
    scores = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            s = similarity(results[i]["lyrics"], results[j]["lyrics"])
            scores[i][j] = scores[j][i] = s
            verdict["pairs"].append(
                (results[i]["source"], results[j]["source"], round(s, 3))
            )

    # Grupo de acuerdo: para cada resultado, con cuántos otros coincide.
    best_idx, best_group = 0, {0}
    for i in range(n):
        group = {i} | {j for j in range(n) if j != i and scores[i][j] >= SIMILARITY_THRESHOLD}
        if len(group) > len(best_group):
            best_idx, best_group = i, group

    if len(best_group) >= 2:
        verdict["validated"] = True
        # Dentro del grupo, elegir la versión más completa (más larga).
        chosen = max((results[i] for i in best_group), key=lambda r: len(r["lyrics"]))
        verdict["chosen"] = chosen
        verdict["agreeing_sources"] = [results[i]["source"] for i in sorted(best_group)]
    else:
        # Sin consenso: se entrega la de la fuente más fiable (orden de consulta)
        verdict["chosen"] = results[0]
        verdict["agreeing_sources"] = [results[0]["source"]]
    return verdict
