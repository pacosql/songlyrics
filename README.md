# songlyrics

App personal: le dices una canción, busca la letra en **varias fuentes
públicas y gratuitas**, la **valida por consenso** entre ellas y genera un
**PDF listo para imprimir en un solo folio** (una columna, como máximo las
dos caras, ajustando el tamaño de letra automáticamente).

Hay dos versiones: una **página web** (sin instalar nada) y una app de
línea de comandos.

## Versión web (GitHub Pages, sin instalar nada)

La app está publicada en **https://pacosql.github.io/songlyrics/**

El archivo `index.html` es una web autónoma que hace todo desde el
navegador: busca en LRCLIB y lyrics.ovh, valida por consenso y descarga
un PDF listo para imprimir en un folio. Se despliega automáticamente con
el workflow de GitHub Actions.

Opcionalmente añade un **glosario al final de la letra** (dos puntos menos
de tamaño): hasta 8 palabras poco comunes de la canción con su traducción
al español (canciones en otro idioma, vía MyMemory) o una breve definición
(canciones en español, vía dictionaryapi.dev), más dos sinónimos y dos
antónimos (vía Datamuse). Todas las fuentes son gratuitas y sin clave.

Nota: ChartLyrics no permite consultas desde el navegador, así que la web
valida con dos fuentes (LRCLIB y lyrics.ovh); la versión de terminal usa
las tres.

## Versión de terminal

### Instalación

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
  APIs públicas y gratuitas (sin registro ni clave de API).
- Si el sistema tiene la fuente DejaVu Sans se usa para soporte Unicode
  completo; si no, se usa Helvetica (suficiente para español).
