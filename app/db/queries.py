from datetime import date
from typing import Optional

from app.models.sighting_models import Sighting


def _build_where(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    city: Optional[str] = None,
    species: Optional[str] = None,
) -> tuple[str, list]:
    clauses, params = [], []
    if date_from:
        clauses.append("date >= ?")
        params.append(date_from.isoformat())               # "2023-01-01" <= "2023-01-01T00:00:00"
    if date_to:
        clauses.append("substr(date, 1, 10) <= ?")          # include the whole end day
        params.append(date_to.isoformat())
    if city:
        clauses.append("location = ? COLLATE NOCASE")
        params.append(city.strip())
    if species:
        clauses.append("species = ? COLLATE NOCASE")
        params.append(species.strip())
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    return where, params


def _row_to_sighting(row) -> Sighting:
    return Sighting(
        id=row["id"], date=row["date"], location=row["location"],
        species=row["species"], latin_name=row["latin_name"],
    )


def upsert_sightings(conn, sightings: list[Sighting]) -> None:
    """Insert new records, update existing ones (same id). Safe to run repeatedly."""
    conn.executemany(
        """INSERT INTO sightings (id, date, location, species, latin_name)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(id) DO UPDATE SET
             date=excluded.date, location=excluded.location,
             species=excluded.species, latin_name=excluded.latin_name""",
        [(s.id, s.date, s.location, s.species, s.latin_name) for s in sightings],
    )


def count_sightings(conn) -> int:
    return conn.execute("SELECT COUNT(*) FROM sightings").fetchone()[0]


def search_sightings(conn, limit, offset, **filters) -> tuple[int, list[Sighting]]:
    where, params = _build_where(**filters)
    total = conn.execute(f"SELECT COUNT(*) FROM sightings {where}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM sightings {where} ORDER BY date DESC, id LIMIT ? OFFSET ?",
        params + [limit, offset],
    ).fetchall()
    return total, [_row_to_sighting(r) for r in rows]


def get_sighting(conn, sighting_id: str) -> Optional[Sighting]:
    row = conn.execute("SELECT * FROM sightings WHERE id = ?", (sighting_id,)).fetchone()
    return _row_to_sighting(row) if row else None


def log_ingestion(conn, started_at, status, fetched=0, accepted=0, rejected=0, message=None):
    conn.execute(
        "INSERT INTO ingestion_log (started_at, status, fetched, accepted, rejected, message) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (started_at, status, fetched, accepted, rejected, message),
    )


def last_ingestion(conn):
    row = conn.execute("SELECT * FROM ingestion_log ORDER BY run_id DESC LIMIT 1").fetchone()
    return dict(row) if row else None