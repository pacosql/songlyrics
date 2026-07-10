# songlyrics

App personal: le dices una canción, busca la letra en **varias fuentes
públicas y gratuitas**, la **valida por consenso** entre ellas y genera un
**PDF listo para imprimir** (una columna, tamaño de letra fijo y legible;
las canciones largas simplemente ocupan más páginas).

Hay dos versiones: una **página web** (sin instalar nada) y una app de
línea de comandos.

## Versión web (GitHub Pages, sin instalar nada)

La app está publicada en **https://pacosql.github.io/songlyrics/**

El archivo `index.html` es una web autónoma que hace todo desde el
navegador: busca en LRCLIB y lyrics.ovh, valida por consenso y descarga
un PDF listo para imprimir. Se despliega automáticamente con el workflow
de GitHub Actions.

El PDF usa la tipografía **Atkinson Hyperlegible** (Braille Institute,
licencia OFL, incrustada en `fonts.js`), con tamaños fijos: letra a 12 pt,
glosario a 10 pt. Nunca se encoge el texto: si la canción es larga, el PDF
tiene más páginas, todas numeradas en el pie.

Incluye un modo **Cancionero**: pegando una lista de canciones (una por
línea, «Canción — Artista») descarga un único PDF con todas — cada canción
empieza en página nueva, con su letra, su glosario y su validación en el
pie de página.

Opcionalmente añade un **glosario que empieza en la cara siguiente a la
letra** (dos puntos menos de tamaño): todas las palabras no triviales de la
canción, en el orden en que aparecen, cada una con su traducción al español,
una definición breve tipo diccionario y dos sinónimos y dos antónimos en
español.

El glosario tiene dos modos:

- **Con IA (opcional)**: pegando una clave de la API de Anthropic en la
  página (se guarda solo en el navegador, en `localStorage`), las
  definiciones se redactan con Claude: lenguaje sencillo para 12 años y
  según el sentido que cada palabra tiene en la canción, con dos sinónimos
  y dos antónimos en español garantizados.
- **Sin clave**: diccionarios gratuitos (MyMemory, dictionaryapi.dev,
  Datamuse) con la acepción principal de cada palabra.

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
- **Tamaño de letra fijo y legible** (12 pt en la web): el texto nunca se
  encoge; las canciones largas ocupan más páginas.
- El pie de página indica qué fuentes validaron la letra, la fecha y el
  número de página.
- (La versión de terminal aún ajusta el tamaño para caber en un folio.)

## Notas

- Uso personal. La app no almacena letras: las consulta en el momento desde
  APIs públicas y gratuitas (sin registro ni clave de API).
- Si el sistema tiene la fuente DejaVu Sans se usa para soporte Unicode
  completo; si no, se usa Helvetica (suficiente para español).
