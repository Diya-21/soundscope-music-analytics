import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("LASTFM_API_KEY")
BASE_URL = "http://ws.audioscrobbler.com/2.0/"


def get_artist_stats(artist_name: str):
    params = {
        "method": "artist.getinfo",
        "artist": artist_name,
        "api_key": API_KEY,
        "format": "json"
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    artist = response.json().get("artist")
    if not artist:
        return None

    stats = artist.get("stats", {})

    return {
        "listeners": int(stats.get("listeners", 0)),
        "playcount": int(stats.get("playcount", 0))
    }
