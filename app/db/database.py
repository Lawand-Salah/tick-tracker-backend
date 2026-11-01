import sqlite3
from contextlib import contextmanager

from app import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS sightings (
    id         TEXT PRIMARY KEY,
    date       TEXT NOT NULL,          -- ISO 8601, sorts correctly as text
    location   TEXT NOT NULL,
    species    TEXT NOT NULL,
    latin_name TEXT
);
CREATE INDEX IF NOT EXISTS idx_sightings_date     ON sightings(date);
CREATE INDEX IF NOT EXISTS idx_sightings_location ON sightings(location);
CREATE INDEX IF NOT EXISTS idx_sightings_species  ON sightings(species);

CREATE TABLE IF NOT EXISTS ingestion_log (
    run_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at  TEXT NOT NULL,
    status      TEXT NOT NULL,         -- ok | failed
    fetched     INTEGER DEFAULT 0,
    accepted    INTEGER DEFAULT 0,
    rejected    INTEGER DEFAULT 0,
    message     TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # rows behave like dicts
    return conn


@contextmanager
def db_session():
    """Open a connection, commit on success, always close."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db_session() as conn:
        conn.executescript(SCHEMA)