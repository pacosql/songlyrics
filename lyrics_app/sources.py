"""Fuentes de letras: cada función devuelve un dict
{"source": str, "lyrics": str, "artist": str, "title": str} o None.

Todas las fuentes son APIs públicas y gratuitas; la app solo consulta
en el momento, no almacena ningún catálogo de letras.
"""

from __future__ import annotations

import urllib.parse
import xml.etree.ElementTree as ET

import requests

TIMEOUT = 15
HEADERS = {"User-Agent": "songlyrics-personal-app/1.0"}


def resolve_song(query: str, artist: str | None = None) -> tuple[str, str] | None:
    """Resuelve (artista, título) canónicos usando la API de búsqueda de iTunes.

    Útil cuando el usuario solo da el nombre de la canción.
    """
    term = f"{artist} {query}" if artist else query
    try:
        r = requests.get(
            "https://itunes.apple.com/search",
            params={"term": term, "entity": "song", "limit": 1},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        results = r.json().get("results", [])
        if results:
            return results[0]["artistName"], results[0]["trackName"]
    except Exception:
        pass
    return None


def fetch_lrclib(artist: str, title: str) -> dict | None:
    """LRCLIB (lrclib.net) — API pública de letras."""
    try:
        r = requests.get(
            "https://lrclib.net/api/get",
            params={"artist_name": artist, "track_name": title},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        if r.status_code == 404:
            # búsqueda difusa como plan B
            r = requests.get(
                "https://lrclib.net/api/search",
                params={"q": f"{artist} {title}"},
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            hits = [h for h in r.json() if h.get("plainLyrics")]
            if not hits:
                return None
            data = hits[0]
        else:
            r.raise_for_status()
            data = r.json()
        lyrics = (data.get("plainLyrics") or "").strip()
        if not lyrics:
            return None
        return {
            "source": "LRCLIB (lrclib.net)",
            "lyrics": lyrics,
            "artist": data.get("artistName", artist),
            "title": data.get("trackName", title),
        }
    except Exception:
        return None


def fetch_lyrics_ovh(artist: str, title: str) -> dict | None:
    """lyrics.ovh — API pública de letras."""
    try:
        url = "https://api.lyrics.ovh/v1/{}/{}".format(
            urllib.parse.quote(artist), urllib.parse.quote(title)
        )
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        lyrics = (r.json().get("lyrics") or "").strip()
        if not lyrics:
            return None
        return {
            "source": "lyrics.ovh",
            "lyrics": lyrics,
            "artist": artist,
            "title": title,
        }
    except Exception:
        return None


def fetch_chartlyrics(artist: str, title: str) -> dict | None:
    """ChartLyrics — API pública SOAP/REST (XML)."""
    try:
        r = requests.get(
            "http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect",
            params={"artist": artist, "song": title},
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return None
        root = ET.fromstring(r.content)
        ns = {"cl": "http://api.chartlyrics.com/"}
        node = root.find("cl:Lyric", ns)
        lyrics = (node.text or "").strip() if node is not None else ""
        if not lyrics:
            return None
        return {
            "source": "ChartLyrics",
            "lyrics": lyrics,
            "artist": artist,
            "title": title,
        }
    except Exception:
        return None


ALL_SOURCES = (fetch_lrclib, fetch_lyrics_ovh, fetch_chartlyrics)


def fetch_all(artist: str, title: str) -> list[dict]:
    """Consulta todas las fuentes y devuelve las que dieron resultado."""
    results = []
    for fetcher in ALL_SOURCES:
        res = fetcher(artist, title)
        if res:
            results.append(res)
    return results
