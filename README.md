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