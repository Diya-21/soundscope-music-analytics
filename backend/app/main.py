from fastapi import FastAPI, Query, HTTPException
from app.musicbrainz import search_artist, get_artist_albums
from app.lastfm import get_artist_stats
from app.database import create_tables, get_connection

app = FastAPI(title="SoundScope – Music Analytics API")

# Initialize database
create_tables()


@app.get("/")
def root():
    return {"message": "SoundScope backend running"}


# -----------------------------
# DATA INGESTION
# -----------------------------
@app.get("/artist/albums")
def fetch_and_store_artist(name: str = Query(..., min_length=2)):
    artist = search_artist(name)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    albums = get_artist_albums(artist["id"])

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO artists VALUES (?, ?, ?)",
        (artist["id"], artist["name"], artist["country"])
    )

    for album in albums:
        cursor.execute(
            """
            INSERT INTO albums (artist_id, title, release_date, type)
            VALUES (?, ?, ?, ?)
            """,
            (
                artist["id"],
                album["title"],
                album.get("first_release_date"),
                album.get("primary_type")
            )
        )

    conn.commit()
    conn.close()

    return {
        "artist": artist["name"],
        "albums_fetched": len(albums),
        "stored": True
    }


# -----------------------------
# ANALYTICS: ALBUMS PER YEAR
# -----------------------------
@app.get("/analytics/albums-per-year")
def albums_per_year(artist_name: str = Query(..., min_length=2)):
    artist = search_artist(artist_name)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT SUBSTR(release_date, 1, 4) AS year, COUNT(*)
        FROM albums
        WHERE artist_id = ?
          AND release_date IS NOT NULL
        GROUP BY year
        ORDER BY year
        """,
        (artist["id"],)
    )

    rows = cursor.fetchall()
    conn.close()

    return {
        "artist": artist["name"],
        "albums_per_year": [
            {"year": row[0], "count": row[1]} for row in rows
        ]
    }


# -----------------------------
# ANALYTICS: ENGAGEMENT SCORE
# -----------------------------
@app.get("/analytics/engagement")
def engagement_analysis(artist_name: str = Query(..., min_length=2)):
    stats = get_artist_stats(artist_name)
    if not stats:
        raise HTTPException(status_code=404, detail="Engagement data not found")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO engagement VALUES (?, ?, ?)",
        (artist_name, stats["listeners"], stats["playcount"])
    )

    cursor.execute(
        """
        SELECT COUNT(*) FROM albums
        WHERE artist_id IN (
            SELECT id FROM artists WHERE name = ?
        )
        """,
        (artist_name,)
    )

    album_count = cursor.fetchone()[0]
    conn.close()

    engagement_score = (
        stats["listeners"] * 0.6 +
        stats["playcount"] * 0.4
    ) / max(album_count, 1)

    return {
        "artist": artist_name,
        "listeners": stats["listeners"],
        "playcount": stats["playcount"],
        "albums": album_count,
        "engagement_score": round(engagement_score, 2)
    }
