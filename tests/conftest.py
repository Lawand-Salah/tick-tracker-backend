import httpx
import pytest

from app import config
from app.db.database import init_db

SAMPLE = [
    {"id": "a1", "date": "2022-03-10T10:00:00", "location": "London", "species": "Marsh tick", "latinName": "Ixodes apronophorus"},
    {"id": "a2", "date": "2022-03-12T11:00:00", "location": "london ", "species": "Marsh tick", "latinName": "Ixodes apronophorus"},
    {"id": "a3", "date": "2023-07-01T08:30:00", "location": "Manchester", "species": "Fox/badger tick", "latinName": "Ixodes canisuga"},
    {"id": "a4", "date": "2023-07-15T09:00:00", "location": "Manchester", "species": "Fox/badger tick", "latinName": None},
    {"id": "a5", "date": "2024-01-05T12:00:00", "location": "Leeds", "species": "Tree-hole tick", "latinName": "Ixodes arboricola"},
]


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATABASE_PATH", tmp_path / "test.db")
    monkeypatch.setattr(config, "RAW_SNAPSHOT_DIR", tmp_path / "raw")
    init_db()
    return tmp_path


def make_client(handler):
    return httpx.Client(transport=httpx.MockTransport(handler))