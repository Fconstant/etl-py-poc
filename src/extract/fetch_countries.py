import logging
import os
from typing import Any

import polars as pl

from src.models.country import CountryModel
from src.utils.http import COUNTRIES_URL, fetch_json

logger = logging.getLogger(__name__)


def fetch_countries() -> pl.DataFrame:
    api_key = os.getenv("REST_COUNTRIES_API_KEY")
    headers: dict[str, str] | None = None
    if api_key:
        headers = {"Authorization": f"Bearer {api_key}"}

    all_objects: list[dict[str, object]] = []
    limit = 100
    offset = 0
    while True:
        url = f"{COUNTRIES_URL}?limit={limit}&offset={offset}"
        resp: Any = fetch_json(url, headers=headers)
        batch: list[dict[str, object]] = resp["data"]["objects"]
        all_objects.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    models: list[CountryModel] = []
    for item in all_objects:
        try:
            models.append(CountryModel.model_validate(item))
        except Exception:
            logger.warning("Skipping invalid country entry: %s", item.get("names", {}))
    rows = [m.model_dump() for m in models]
    return pl.DataFrame(rows) if rows else pl.DataFrame()
