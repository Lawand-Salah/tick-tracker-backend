from pathlib import Path
import os

#Project root directory that contains app/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

#APi configuration
EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://dev-task.elancoapps.com/data")
API_TIMEOUT_SECONDS = float(os.getenv("API_TIMEOUT_SECONDS", 10))
API_MAX_RETRIES = int(os.getenv("API_MAX_RETRIES", 4))
API_BACKOFF_SECONDS = float(os.getenv("API_BACKOFF_SECONDS", 1.0))

#Database configuration
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", PROJECT_ROOT / "data" / "ticks.db"))

#Directory for storing raw snapshots of the external API data
RAW_SNAPSHOT_DIR = PROJECT_ROOT / "data" / "raw"

