import logging
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

HTTP_TIMEOUT = 10.0
MAX_RETRIES = 3
COUNTRIES_URL = "https://api.restcountries.com/countries/v5"
UNIVERSITIES_URL = "http://universities.hipolabs.com/search"


def fetch_json(url: str, headers: dict[str, str] | None = None) -> Any:  # noqa: ANN401
    client = httpx.Client(timeout=HTTP_TIMEOUT)

    for attempt in range(MAX_RETRIES):
        try:
            response = client.get(url, headers=headers)
            if response.status_code >= 500:
                response.raise_for_status()
            response.raise_for_status()
            return response.json()  # type: ignore[no-any-return]
        except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
            if isinstance(e, httpx.HTTPStatusError) and e.response.status_code < 500:
                raise
            if attempt == MAX_RETRIES - 1:
                msg = f"Request failed after {MAX_RETRIES} retries"
                raise RuntimeError(msg) from e
            wait = 2**attempt
            logger.warning(
                "Request failed (attempt %d/%d), retrying in %ds: %s",
                attempt + 1,
                MAX_RETRIES,
                wait,
                e,
            )
            time.sleep(wait)

    msg = "Unreachable"
    raise RuntimeError(msg)  # pragma: no cover
