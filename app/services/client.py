from typing import Optional
import httpx
from app.config import API_TIMEOUT_SECONDS, EXTERNAL_API_URL

class ElancoAPIError(Exception):
    """Raise when the Elanco API returns a non-usable data"""

def fetch_all_sightings(http_client: Optional[httpx.Client] = None)-> list[dict]:
    """Return the raw list of sightings from GET /tick-sightings."""
    url = f"{EXTERNAL_API_URL.rstrip('/')}/tick-sightings"
    own_client = http_client is None
    client = http_client or httpx.Client(timeout=API_TIMEOUT_SECONDS)
    try:
        response = client.get(url)
    except (httpx.TimeoutException, httpx.TransportError) as exc:
        raise ElancoAPIError(f"network error: {exc.__class__.__name__}")
    finally:
        if own_client:
            client.close()

    if response.status_code != 200:
        raise ElancoAPIError(f"Elanco API returned status {response.status_code}")
    data = response.json()
    if not isinstance(data, list):
        raise ElancoAPIError("Elanco API returned unexpected shape (expected a list)")
    return data