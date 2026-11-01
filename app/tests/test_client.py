import httpx
import pytest

from app.services.client import ElancoAPIError, fetch_all_sightings
from tests.conftest import make_client


def test_returns_data_on_success():
    http = make_client(lambda req: httpx.Response(200, json=[{"id": "1"}]))
    assert fetch_all_sightings(http) == [{"id": "1"}]


def test_error_status_raises_clear_error():
    http = make_client(lambda req: httpx.Response(500, json={"error": "boom"}))
    with pytest.raises(ElancoAPIError):
        fetch_all_sightings(http)


def test_bad_json_shape_raises():
    http = make_client(lambda req: httpx.Response(200, json={"not": "a list"}))
    with pytest.raises(ElancoAPIError):
        fetch_all_sightings(http)