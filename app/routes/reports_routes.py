from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, Query

from app.models.sighting_models import CountByKey, TrendResponse
from app.routes.sightings_routes import check_date_range
from app.services import report_service

router = APIRouter()


@router.get("/by-city", response_model=list[CountByKey])
def sightings_per_region(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    species: Optional[str] = None,
):
    check_date_range(date_from, date_to)
    return report_service.sightings_by_city(date_from=date_from, date_to=date_to, species=species)


@router.get("/by-species", response_model=list[CountByKey])
def sightings_per_species(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    city: Optional[str] = None,
):
    check_date_range(date_from, date_to)
    return report_service.sightings_by_species(date_from=date_from, date_to=date_to, city=city)


@router.get("/trends", response_model=TrendResponse)
def trends_over_time(
    period: Literal["weekly", "monthly"] = Query("monthly"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    city: Optional[str] = None,
    species: Optional[str] = None,
):
    check_date_range(date_from, date_to)
    return report_service.trends(
        period, date_from=date_from, date_to=date_to, city=city, species=species
    )