import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import queries
from app.db.database import db_session, init_db
from app.routes import admin_routes, sightings_routes
from app.services.ingestion_service import run_ingestion

logger = logging.getLogger("tick-tracker")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with db_session() as conn:
        empty = queries.count_sightings(conn) == 0
    if empty:
        summary = run_ingestion()  # never raises: failures come back as a summary
        logger.info("Initial ingestion: %s", summary.model_dump())
    yield


app = FastAPI(
    title="Tick Sightings Backend",
    description="Consumes the Elanco tick sightings API, cleans and stores it, "
                "and exposes search, filter and reporting endpoints.",
    lifespan=lifespan,
)

app.include_router(sightings_routes.router, prefix="/sightings", tags=["Sightings"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])


@app.get("/health", tags=["Admin"])
def health():
    return {"status": "healthy"}