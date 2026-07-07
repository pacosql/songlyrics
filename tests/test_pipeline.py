"""Tests sin red: validación cruzada y ajuste del PDF a un folio.

Se usa texto sintético (no letras reales) para poder probar sin
depender de las APIs externas.
"""

import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lyrics_app.validator import validate, similarity  # noqa: E402
from lyrics_app.pdf import build_pdf, MAX_PAGES  # noqa: E402

WORDS = ("luna", "camino", "viento", "canta", "sombra", "río",
         "fuego", "cielo", "baila", "tiempo", "voz", "mar")


def fake_lyrics(lines: int, seed: int = 1) -> str:
    rng = random.Random(seed)
    out = []
    for i in range(lines):
        if i and i % 6 == 0:
            out.append("")
        out.append(" ".join(rng.choice(WORDS) for _ in range(rng.randint(4, 7))))
    return "\n".join(out)


def variant(text: str) -> str:
    """Versión con pequeñas diferencias de formato, como daría otra fuente."""
    return text.upper().replace("\n\n", "\n \n") + "\n[Coro]"


class ValidatorTests(unittest.TestCase):
    def test_two_agreeing_sources_validate(self):
        base = fake_lyrics(24)
        results = [
            {"source": "A", "lyrics": base, "artist": "x", "title": "y"},
            {"source": "B", "lyrics": variant(base), "artist": "x", "title": "y"},
            {"source": "C", "lyrics": fake_lyrics(24, seed=99), "artist": "x", "title": "y"},
        ]
        v = validate(results)
        self.assertTrue(v["validated"])
        self.assertEqual(sorted(v["agreeing_sources"]), ["A", "B"])
        self.assertIn(v["chosen"]["source"], ("A", "B"))

    def test_single_source_not_validated(self):
        v = validate([{"source": "A", "lyrics": fake_lyrics(10), "artist": "x", "title": "y"}])
        self.assertFalse(v["validated"])
        self.assertIsNotNone(v["chosen"])

    def test_disagreeing_sources_not_validated(self):
        v = validate([
            {"source": "A", "lyrics": fake_lyrics(20, seed=1), "artist": "x", "title": "y"},
            {"source": "B", "lyrics": fake_lyrics(20, seed=2), "artist": "x", "title": "y"},
        ])
        self.assertFalse(v["validated"])

    def test_similarity_ignores_case_accents_punctuation(self):
        self.assertGreater(similarity("¡La luna canta, río!", "la luna canta rio"), 0.95)


class PdfTests(unittest.TestCase):
    def _build(self, lines: int) -> dict:
        verdict = {"validated": True, "agreeing_sources": ["A", "B"]}
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "out.pdf")
            info = build_pdf("Título de Prueba", "Artista Ñandú",
                             fake_lyrics(lines), verdict, path)
            self.assertTrue(os.path.getsize(path) > 500)
            with open(path, "rb") as fh:
                self.assertEqual(fh.read(5), b"%PDF-")
        return info

    def test_short_song_one_side(self):
        info = self._build(24)
        self.assertEqual(info["pages"], 1)
        self.assertTrue(info["fits"])

    def test_long_song_fits_one_sheet_by_shrinking(self):
        info = self._build(120)
        self.assertLessEqual(info["pages"], MAX_PAGES)
        self.assertTrue(info["fits"])
        self.assertLess(info["font_size"], 12)

    def test_extreme_song_reported_as_not_fitting(self):
        info = self._build(600)
        if info["pages"] > MAX_PAGES:
            self.assertFalse(info["fits"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
