# songlyrics

App personal de línea de comandos: le dices una canción, busca la letra en
**varias fuentes públicas**, la **valida por consenso** entre ellas y genera
un **PDF listo para imprimir en un solo folio** (usa como máximo las dos
caras, ajustando el tamaño de letra automáticamente).

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Solo con el nombre de la canción (identifica el artista automáticamente)
python -m lyrics_app "Bohemian Rhapsody"

# Afinando con el artista y eligiendo el nombre del PDF
python -m lyrics_app "Clavado en un bar" -a "Maná" -o clavado.pdf
```

## Cómo valida la letra

1. Consulta tres fuentes públicas: **LRCLIB**, **lyrics.ovh** y **ChartLyrics**.
2. Normaliza los textos (minúsculas, sin tildes ni puntuación) y los compara
   por pares con un índice de similitud.
3. Si **dos o más fuentes coinciden** por encima del umbral (72 %), la letra
   se marca como *validada* y se usa la versión más completa del grupo que
   coincide. Si solo responde una fuente o no hay consenso, el PDF lo indica
   en el pie de página para que la revises antes de imprimir.

## El PDF

- Formato A4, **una sola columna**, título y artista en cabecera, letra
  centrada.
- **Máximo un folio (2 páginas, cara y dorso)**: el tamaño de letra baja
  automáticamente de 12 pt hasta 7 pt hasta que quepa. Si ni así cabe,
  se genera igualmente y la app avisa.
- El pie de página indica qué fuentes validaron la letra y la fecha.

## Notas

- Uso personal. La app no almacena letras: las consulta en el momento desde
  APIs públicas.
- Si el sistema tiene la fuente DejaVu Sans se usa para soporte Unicode
  completo; si no, se usa Helvetica (suficiente para español).
