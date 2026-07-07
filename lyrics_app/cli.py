"""CLI: python -m lyrics_app "Nombre de la canción" [-a Artista] [-o salida.pdf]"""

from __future__ import annotations

import argparse
import re
import sys

from . import sources, validator
from .pdf import build_pdf


def _slug(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip()
    return re.sub(r"[\s_-]+", "-", text) or "cancion"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lyrics_app",
        description="Busca la letra de una canción en varias fuentes, "
        "la valida por consenso y genera un PDF listo para imprimir.",
    )
    parser.add_argument("song", help="Nombre de la canción")
    parser.add_argument("-a", "--artist", help="Artista (recomendado para afinar)")
    parser.add_argument("-o", "--output", help="Ruta del PDF de salida")
    args = parser.parse_args(argv)

    artist, title = args.artist, args.song

    # Si falta el artista (o para canonizar), resolver con iTunes Search.
    resolved = sources.resolve_song(args.song, args.artist)
    if resolved:
        artist, title = resolved
        print(f"♪ Canción identificada: “{title}” — {artist}")
    elif not artist:
        print(
            "No pude identificar el artista automáticamente. "
            "Vuelve a intentarlo con -a/--artist.",
            file=sys.stderr,
        )
        return 2
    else:
        print(f"♪ Buscando: “{title}” — {artist}")

    print("Consultando fuentes (LRCLIB, lyrics.ovh, ChartLyrics)…")
    results = sources.fetch_all(artist, title)
    if not results:
        print("✗ Ninguna fuente devolvió la letra. Revisa el título/artista.", file=sys.stderr)
        return 1
    for r in results:
        print(f"  ✓ {r['source']}: {len(r['lyrics'])} caracteres")

    verdict = validator.validate(results)
    if verdict["pairs"]:
        for a, b, s in verdict["pairs"]:
            print(f"  · similitud {a} ↔ {b}: {s:.0%}")
    if verdict["validated"]:
        print(f"✔ Letra VALIDADA por {len(verdict['agreeing_sources'])} fuentes: "
              f"{', '.join(verdict['agreeing_sources'])}")
    else:
        print("⚠ Solo una fuente disponible o sin consenso; se usa la mejor versión "
              f"({verdict['chosen']['source']}). Revísala antes de imprimir.")

    chosen = verdict["chosen"]
    output = args.output or f"{_slug(artist)}-{_slug(title)}.pdf"
    info = build_pdf(chosen.get("title", title), chosen.get("artist", artist),
                     chosen["lyrics"], verdict, output)
    caras = "cara" if info["pages"] == 1 else "caras"
    print(f"📄 PDF generado: {info['path']} "
          f"({info['pages']} {caras} de un folio, letra a {info['font_size']} pt)")
    if not info["fits"]:
        print("⚠ La letra es muy larga: no cabe en un folio ni con la letra "
              "mínima. El PDF tiene más de 2 páginas.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
