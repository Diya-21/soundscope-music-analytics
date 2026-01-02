import requests

BASE_URL = "https://musicbrainz.org/ws/2"
HEADERS = {
    "User-Agent": "SoundScope/1.0 (analytics-project)"
}


def search_artist(artist_name: str):
    url = f"{BASE_URL}/artist"
    params = {
        "query": artist_name,
        "fmt": "json",
        "limit": 1
    }

    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()

    artists = response.json().get("artists", [])
    if not artists:
        return None

    artist = artists[0]
    return {
        "id": artist["id"],
        "name": artist["name"],
        "country": artist.get("country")
    }


def get_artist_albums(artist_id: str):
    url = f"{BASE_URL}/release-group"
    params = {
        "artist": artist_id,
        "fmt": "json",
        "limit": 50,
        "type": "album"
    }

    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()

    albums = []
    for item in response.json().get("release-groups", []):
        albums.append({
            "title": item["title"],
            "first_release_date": item.get("first-release-date"),
            "primary_type": item.get("primary-type")
        })

    return albums
