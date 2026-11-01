
from typing import Optional

from pydantic import BaseModel, Field


class RawSighting(BaseModel):
    id: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    species: Optional[str] = None
    latinName: Optional[str] = None


class Sighting(BaseModel):
    id: str
    date: str            # ISO format: YYYY-MM-DDTHH:MM:SS
    location: str        # normalised city name, e.g. "Manchester"
    species: str
    latin_name: Optional[str] = None


class SightingPage(BaseModel):
    total: int = Field(description="Total records matching the filters")
    limit: int
    offset: int
    results: list[Sighting]


class CountByKey(BaseModel):
    key: str
    count: int


class TrendPoint(BaseModel):
    period: str          # e.g. "2023-07" (monthly) or "2023-W27" (weekly)
    count: int


class TrendResponse(BaseModel):
    period_type: str
    points: list[TrendPoint]


class IngestionSummary(BaseModel):
    status: str                      # "ok" | "stale" | "failed"
    fetched: int = 0
    accepted: int = 0
    rejected: int = 0
    duplicates_removed: int = 0
    incomplete_kept: int = 0
    rejection_reasons: dict[str, int] = {}
    message: Optional[str] = None