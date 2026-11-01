import json
from datetime import datetime

from app import config
from app.db import queries
from app.db.database import db_session
from app.models.sighting_models import IngestionSummary
from app.services.cleaning_service import clean_sightings
from app.services.client import ElancoAPIError, fetch_all_sightings


def _save_raw_snapshot(raw: list[dict]) -> None:
    try:
        config.RAW_SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        (config.RAW_SNAPSHOT_DIR / "latest_snapshot.json").write_text(json.dumps(raw))
    except OSError:
        pass  # a failed snapshot must never break ingestion


def run_ingestion(http_client=None) -> IngestionSummary:
    started = datetime.now().isoformat(timespec="seconds")

    try:
        raw = fetch_all_sightings(http_client)
    except ElancoAPIError as exc:
        with db_session() as conn:
            existing = queries.count_sightings(conn)
            queries.log_ingestion(conn, started, "failed", message=str(exc))
        status = "stale" if existing else "failed"
        note = (
            f"{exc}. Serving {existing} previously stored records."
            if existing else f"{exc}. No stored data available yet."
        )
        return IngestionSummary(status=status, message=note)

    _save_raw_snapshot(raw)
    result = clean_sightings(raw)
    stats = result["stats"]

    with db_session() as conn:
        queries.upsert_sightings(conn, result["clean"])
        queries.log_ingestion(
            conn, started, "ok",
            fetched=stats["fetched"], accepted=stats["accepted"], rejected=stats["rejected"],
        )
    return IngestionSummary(status="ok", **stats)