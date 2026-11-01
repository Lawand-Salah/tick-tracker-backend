from app.db import queries
from app.db.database import db_session
from app.models.sighting_models import IngestionSummary
from app.services.cleaning_service import clean_sightings
from app.services.client import fetch_all_sightings


def run_ingestion(http_client=None) -> IngestionSummary:
    raw = fetch_all_sightings(http_client)   # may raise ElancoAPIError (handled in the next commit)
    result = clean_sightings(raw)
    with db_session() as conn:
        queries.upsert_sightings(conn, result["clean"])
    return IngestionSummary(status="ok", **result["stats"])