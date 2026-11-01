from fastapi import APIRouter, Response

from app.db import queries
from app.db.database import db_session
from app.models.sighting_models import IngestionSummary
from app.services.ingestion_service import run_ingestion

router = APIRouter()


@router.post("/refresh", response_model=IngestionSummary)
def refresh_data(response: Response):
    summary = run_ingestion()
    if summary.status == "failed":
        response.status_code = 502
    return summary


@router.get("/status")
def status():
    with db_session() as conn:
        return {
            "stored_sightings": queries.count_sightings(conn),
            "last_ingestion": queries.last_ingestion(conn),
        }