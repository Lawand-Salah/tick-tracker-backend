import httpx
import pytest

from app.services import client as client_module
from app.services.client import ElancoAPIError, fetch_all_sightings
from tests.conftest import make_client


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(client_module.time, "sleep", lambda s: None)


def test_returns_data_on_success():
    http = make_client(lambda req: httpx.Response(200, json=[{"id": "1"}]))
    assert fetch_all_sightings(http) == [{"id": "1"}]


def test_retries_on_429_then_succeeds():
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        return httpx.Response(429, json={"error": "rate"}) if calls["n"] < 3 else httpx.Response(200, json=[])

    assert fetch_all_sightings(make_client(handler)) == []
    assert calls["n"] == 3


def test_gives_clear_error_after_repeated_500s():
    http = make_client(lambda req: httpx.Response(500, json={"error": "boom"}))
    with pytest.raises(ElancoAPIError, match="after"):
        fetch_all_sightings(http)


def test_404_is_not_retried():
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        return httpx.Response(404)

    with pytest.raises(ElancoAPIError):
        fetch_all_sightings(make_client(handler))
    assert calls["n"] == 1


def test_bad_json_shape_raises():
    http = make_client(lambda req: httpx.Response(200, json={"not": "a list"}))
    with pytest.raises(ElancoAPIError):
        fetch_all_sightings(http)


def test_timeout_is_retried_then_fails():
    def handler(req):
        raise httpx.ConnectTimeout("slow")

    with pytest.raises(ElancoAPIError, match="network error"):
        fetch_all_sightings(make_client(handler))