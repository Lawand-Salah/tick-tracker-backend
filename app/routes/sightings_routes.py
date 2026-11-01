from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.db import queries
from app.db.database import db_session
from app.models.sighting_models import Sighting, SightingPage

router = APIRouter()


def check_date_range(date_from: Optional[date], date_to: Optional[date]) -> None:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="'date_from' must not be after 'date_to'")


@router.get("", response_model=SightingPage)
def search_sightings(
    date_from: Optional[date] = Query(None, description="Start date, YYYY-MM-DD (inclusive)"),
    date_to: Optional[date] = Query(None, description="End date, YYYY-MM-DD (inclusive)"),
    city: Optional[str] = Query(None, description="City name, case-insensitive, e.g. Manchester"),
    species: Optional[str] = Query(None, description="Species name, case-insensitive"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Search and filter sightings by time range, location and species (paginated)."""
    check_date_range(date_from, date_to)
    with db_session() as conn:
        total, results = queries.search_sightings(
            conn, limit, offset,
            date_from=date_from, date_to=date_to, city=city, species=species,
        )
    return SightingPage(total=total, limit=limit, offset=offset, results=results)


@router.get("/{sighting_id}", response_model=Sighting)
def get_sighting(sighting_id: str):
    with db_session() as conn:
        sighting = queries.get_sighting(conn, sighting_id)
    if sighting is None:
        raise HTTPException(status_code=404, detail="Sighting not found")
    return sighting