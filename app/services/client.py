"""Handles the failure modes the API documents:
  * 429 - rate limited        -> wait and retry
  * 500 - server error        -> retry with exponential backoff
  * timeouts / network errors -> retry
Anything else (e.g. 404, 400) is not retried because retrying won't help.
"""
import time
from typing import Optional

import httpx

from app.config import (
    API_BACKOFF_SECONDS,
    API_MAX_RETRIES,
    API_TIMEOUT_SECONDS,
    EXTERNAL_API_URL,
)

RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class ElancoAPIError(Exception):
    """Raised when the API cannot give us usable data."""


def _wait_time(attempt: int, response: Optional[httpx.Response]) -> float:
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after and retry_after.isdigit():
            return float(retry_after)
    return API_BACKOFF_SECONDS * (2 ** (attempt - 1))


def fetch_all_sightings(http_client: Optional[httpx.Client] = None) -> list[dict]:
    url = f"{EXTERNAL_API_URL.rstrip('/')}/tick-sightings"
    own_client = http_client is None
    client = http_client or httpx.Client(timeout=API_TIMEOUT_SECONDS)
    last_problem = "unknown error"

    try:
        for attempt in range(1, API_MAX_RETRIES + 1):
            response = None
            try:
                response = client.get(url)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_problem = f"network error: {exc.__class__.__name__}"
            else:
                if response.status_code == 200:
                    try:
                        data = response.json()
                    except ValueError:
                        raise ElancoAPIError("API returned invalid JSON")
                    if not isinstance(data, list):
                        raise ElancoAPIError("API returned unexpected shape (expected a list)")
                    return data
                if response.status_code not in RETRYABLE_STATUS:
                    raise ElancoAPIError(
                        f"API returned status {response.status_code} (not retryable)"
                    )
                last_problem = f"status {response.status_code}"

            if attempt < API_MAX_RETRIES:
                time.sleep(_wait_time(attempt, response))
    finally:
        if own_client:
            client.close()

    raise ElancoAPIError(
        f"API unavailable after {API_MAX_RETRIES} attempts (last problem: {last_problem})"
    )