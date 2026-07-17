import logging

import polars as pl

from src.models.country import CountryModel
from src.utils.http import COUNTRIES_URL, fetch_json

logger = logging.getLogger(__name__)


def fetch_countries() -> pl.DataFrame:
    data = fetch_json(COUNTRIES_URL)
    models: list[CountryModel] = []
    for item in data:
        try:
            models.append(CountryModel.model_validate(item))
        except Exception:
            logger.warning("Skipping invalid country entry: %s", item.get("name", {}))
    rows = [m.model_dump() for m in models]
    return pl.DataFrame(rows) if rows else pl.DataFrame()
