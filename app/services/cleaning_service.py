from collections import Counter
from datetime import datetime
from typing import Optional

from pydantic import ValidationError

from app.models.sighting_models import RawSighting, Sighting


def _clean_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = " ".join(str(value).split())  # trim + collapse inner whitespace
    return value or None


def _parse_date(value: str) -> Optional[datetime]:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is not None:  # the API sends naive datetimes; store them naive
        parsed = parsed.replace(tzinfo=None)
    return parsed


def clean_sightings(raw_records: list[dict], now: Optional[datetime] = None) -> dict:
    """Return {"clean": [Sighting...], "stats": {...}}."""
    now = now or datetime.now()
    reasons: Counter = Counter()
    clean: list[Sighting] = []
    duplicates = 0  # duplicate removal is added in the next commit
    incomplete = 0

    for item in raw_records:
        if not isinstance(item, dict):
            reasons["record is not an object"] += 1
            continue
        try:
            raw = RawSighting.model_validate(item)
        except ValidationError:
            reasons["wrong field types"] += 1
            continue

        rec_id = _clean_text(raw.id)
        location = _clean_text(raw.location)
        species = _clean_text(raw.species)
        latin = _clean_text(raw.latinName)
        date_text = _clean_text(raw.date)

        if not rec_id:
            reasons["missing id"] += 1
            continue
        if not date_text:
            reasons["missing date"] += 1
            continue
        if not location:
            reasons["missing location"] += 1
            continue
        if not species:
            reasons["missing species"] += 1
            continue

        parsed = _parse_date(date_text)
        if parsed is None:
            reasons["unparseable date"] += 1
            continue
        if parsed > now:
            reasons["date in the future"] += 1
            continue

        location = location.title()
        if latin is None:
            incomplete += 1

        clean.append(
            Sighting(
                id=rec_id,
                date=parsed.isoformat(timespec="seconds"),
                location=location,
                species=species,
                latin_name=latin,
            )
        )

    stats = {
        "fetched": len(raw_records),
        "accepted": len(clean),
        "rejected": sum(reasons.values()),
        "duplicates_removed": duplicates,
        "incomplete_kept": incomplete,
        "rejection_reasons": dict(reasons),
    }
    return {"clean": clean, "stats": stats}