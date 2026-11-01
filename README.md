# Tick Sightings Backend (Elanco ITSP Task – Backend)

**Author: Lawand Salah**

A FastAPI backend that consumes the Elanco tick-sightings API, cleans and stores the data in SQLite, and exposes
endpoints to search/filter sightings and to report aggregate insights.

## How to run

```bash
python -m venv .venv            # create a virtual environment (kept out of git)
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** for interactive API docs.
On first start the app creates `data/ticks.db` and loads the data from the Elanco API automatically.

Run the tests: `python -m pytest -q`
Run the data audit: `python -m scripts.audit_data`

Optional settings (API URL, retries, DB path) can be changed via environment variables – see `.env.example`. -- Hasn't been implemented into the program yet

## Endpoints

| Method | Path | What it does |
|---|---|---|
| GET | `/sightings` | Search/filter by `date_from`, `date_to`, `city`, `species`; paginated (`limit`, `offset`) |
| GET | `/sightings/{id}` | One sighting (404 if unknown) |
| GET | `/reports/by-city` | Number of sightings per region (optional date/species filters) |
| GET | `/reports/by-species` | Number of sightings per species |
| GET | `/reports/trends?period=weekly\|monthly` | Sightings over time (optional city/species/date filters) |
| GET | `/reports/insights` | Extension: statistical insights (unusual months, peak season, hotspot) |
| POST | `/admin/refresh` | Re-fetch from Elanco, clean, store |
| GET | `/admin/status` | Stored row count + result of the last ingestion run |
| GET | `/health` | Health check |


* **Fetch once, store locally, query our own copy.** The upstream API has no date filter or pagination and is rate
  limited (429), so calling it per request would be slow and fragile. We ingest into SQLite and serve everything from there.
* **SQLite** (standard library, zero setup) lets us filter by date/city and `GROUP BY` for reports with real SQL and indexes.
* **Layers:** `routes/` (HTTP only) -> `services/` (logic) -> `db/` (SQL). `models/` holds Pydantic models.
* **FastAPI + Pydantic** give validation, automatic docs and clear error codes (400 bad range, 404 not found, 422 bad format).

## Data handling plan

1. **Audit first** (`scripts/audit_data.py`): count records, duplicates, missing fields, odd names, date range.
2. **Validate/clean** every record (`cleaning_service.py`):
   * required fields: `id`, `date`, `location`, `species` – otherwise rejected (reason counted);
   * dates must parse and not be in the future;
   * whitespace trimmed and city names normalised (`"  manchester "` -> `Manchester`);
   * `latinName` missing -> record **kept** and counted as incomplete (it is still useful for counts);
   * duplicates removed (same `id`, or same date + location + species); first one wins.
3. **Store idempotently:** `INSERT ... ON CONFLICT(id) DO UPDATE`, so refreshing never creates duplicates.
4. **Report:** every ingestion returns `fetched / accepted / rejected / duplicates / reasons` and is logged in `ingestion_log`.

## Error handling

* `client.py` retries on 429, 500/502/503/504, timeouts and network errors with exponential backoff
  (honours `Retry-After`); non-retryable errors (e.g. 404) fail immediately; malformed JSON is detected.
* After the last attempt it raises a clear `ElancoAPIError` – never returns `None` silently.
* If Elanco is down, the app **keeps serving the data already stored** and `/admin/refresh` reports `"status": "stale"`.
  Only if there is no stored data at all does it return **502**.
* Bad user input gives clear errors instead of crashes (e.g. `date_from` after `date_to` -> 400).
* A raw copy of every API response is saved to `data/raw/latest_snapshot.json` for debugging.

## AI/ML insights (extension)

Hasn't been implemented into the program yet...

## Tests

`tests/` covers the cleaning rules, the retry logic (using a fake HTTP transport), and the API endpoints including the
"Elanco is down" scenarios.

## What I would do with more time

* Scheduled background refresh (e.g. every hour) and incremental updates.
* Geographic coordinates / map-ready endpoints, and a proper region grouping (e.g. England/Scotland/Wales).
* Caching of report results, authentication for `/admin`, and a migration tool for the DB schema.
* Docker setup and CI to run tests on every push.
* A better ML model (e.g. forecasting seasonal trends) once more data features are available.
* Implement the AI/ML into the program.

