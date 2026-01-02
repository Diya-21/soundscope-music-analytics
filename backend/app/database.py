import sqlite3

DB_NAME = "soundscope.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artists (
        id TEXT PRIMARY KEY,
        name TEXT,
        country TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS albums (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_id TEXT,
        title TEXT,
        release_date TEXT,
        type TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS engagement (
        artist_name TEXT PRIMARY KEY,
        listeners INTEGER,
        playcount INTEGER
    )
    """)

    conn.commit()
    conn.close()
