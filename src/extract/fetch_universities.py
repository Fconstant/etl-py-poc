import logging

import polars as pl

from src.models.university import UniversityModel
from src.utils.http import UNIVERSITIES_URL, fetch_json

logger = logging.getLogger(__name__)


def fetch_universities() -> pl.DataFrame:
    data = fetch_json(UNIVERSITIES_URL)
    models: list[UniversityModel] = []
    for item in data:
        try:
            models.append(UniversityModel.model_validate(item))
        except Exception:
            logger.warning(
                "Skipping invalid university entry: %s", item.get("name", "")
            )
    rows = [m.model_dump() for m in models]
    return pl.DataFrame(rows) if rows else pl.DataFrame()
