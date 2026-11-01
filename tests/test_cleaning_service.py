from datetime import datetime

from app.services.cleaning_service import clean_sightings

NOW = datetime(2026, 1, 1)


def rec(**kw):
    base = {"id": "x", "date": "2020-01-01T00:00:00", "location": "London",
            "species": "Marsh tick", "latinName": "Ixodes apronophorus"}
    base.update(kw)
    return base


def test_valid_record_is_kept():
    out = clean_sightings([rec()], now=NOW)
    assert out["stats"]["accepted"] == 1 and out["stats"]["rejected"] == 0


def test_missing_required_fields_rejected_with_reason():
    out = clean_sightings([rec(id=None), rec(id="b", location=""), rec(id="c", date=None)], now=NOW)
    assert out["stats"]["accepted"] == 0
    assert out["stats"]["rejection_reasons"] == {
        "missing id": 1, "missing location": 1, "missing date": 1}


def test_bad_and_future_dates_rejected():
    out = clean_sightings([rec(id="1", date="not a date"), rec(id="2", date="2030-01-01T00:00:00")], now=NOW)
    assert out["stats"]["rejection_reasons"] == {"unparseable date": 1, "date in the future": 1}


def test_city_normalised_and_missing_latin_name_kept():
    out = clean_sightings([rec(location="  manchester ", latinName=None)], now=NOW)
    s = out["clean"][0]
    assert s.location == "Manchester" and s.latin_name is None
    assert out["stats"]["incomplete_kept"] == 1


def test_non_dict_record_rejected():
    out = clean_sightings(["oops", 5], now=NOW)
    assert out["stats"]["rejected"] == 2