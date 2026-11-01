from app.db import queries
from app.db.database import db_session


def sightings_by_city(**filters) -> list[dict]:
    with db_session() as conn:
        return [{"key": k, "count": n} for k, n in queries.count_by(conn, "location", **filters)]


def sightings_by_species(**filters) -> list[dict]:
    with db_session() as conn:
        return [{"key": k, "count": n} for k, n in queries.count_by(conn, "species", **filters)]


def trends(period: str, **filters) -> dict:
    with db_session() as conn:
        rows = queries.count_by_period(conn, period, **filters)
    return {"period_type": period, "points": [{"period": p, "count": n} for p, n in rows]}