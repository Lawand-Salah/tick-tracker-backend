import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import client as client_module
from app.services import ingestion_service
from tests.conftest import SAMPLE


@pytest.fixture()
def api(temp_db, monkeypatch):
    monkeypatch.setattr(ingestion_service, "fetch_all_sightings", lambda http_client=None: SAMPLE)
    with TestClient(app) as c:   # startup ingests SAMPLE because the DB is empty
        yield c


def test_startup_loads_and_cleans_data(api):
    s = api.get("/admin/status").json()
    assert s["stored_sightings"] == 5
    assert s["last_ingestion"]["status"] == "ok"


def test_search_filters_by_city_case_insensitive(api):
    r = api.get("/sightings", params={"city": "MANCHESTER"}).json()
    assert r["total"] == 2


def test_search_filters_by_time_range(api):
    r = api.get("/sightings", params={"date_from": "2023-01-01", "date_to": "2023-12-31"}).json()
    assert r["total"] == 2 and all(x["date"].startswith("2023") for x in r["results"])


def test_end_date_is_inclusive(api):
    r = api.get("/sightings", params={"date_from": "2023-07-15", "date_to": "2023-07-15"}).json()
    assert r["total"] == 1


def test_pagination(api):
    r = api.get("/sightings", params={"limit": 2, "offset": 0}).json()
    assert len(r["results"]) == 2 and r["total"] == 5


def test_bad_range_returns_400(api):
    assert api.get("/sightings", params={"date_from": "2024-01-01", "date_to": "2023-01-01"}).status_code == 400


def test_bad_date_format_returns_422(api):
    assert api.get("/sightings", params={"date_from": "yesterday"}).status_code == 422


def test_get_by_id_and_404(api):
    assert api.get("/sightings/a3").json()["location"] == "Manchester"
    assert api.get("/sightings/nope").status_code == 404


def test_refresh_when_elanco_down_serves_stale_data(api, monkeypatch):
    def boom(http_client=None):
        raise client_module.ElancoAPIError("down")
    monkeypatch.setattr(ingestion_service, "fetch_all_sightings", boom)
    r = api.post("/admin/refresh")
    assert r.status_code == 200 and r.json()["status"] == "stale"
    assert api.get("/sightings").json()["total"] == 5   # data still served


def test_refresh_when_down_and_empty_returns_502(temp_db, monkeypatch):
    def boom(http_client=None):
        raise client_module.ElancoAPIError("down")
    monkeypatch.setattr(ingestion_service, "fetch_all_sightings", boom)
    with TestClient(app) as c:
        assert c.post("/admin/refresh").status_code == 502
        assert c.get("/sightings").json()["total"] == 0

def test_by_city_report(api):
    data = {d["key"]: d["count"] for d in api.get("/reports/by-city").json()}
    assert data == {"London": 2, "Manchester": 2, "Leeds": 1}


def test_trends_monthly_and_weekly(api):
    m = api.get("/reports/trends", params={"period": "monthly"}).json()
    assert {"period": "2022-03", "count": 2} in m["points"]
    w = api.get("/reports/trends", params={"period": "weekly"}).json()
    assert w["period_type"] == "weekly" and len(w["points"]) >= 3
    assert api.get("/reports/trends", params={"period": "daily"}).status_code == 422