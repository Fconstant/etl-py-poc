import logging
import os
import time
from collections.abc import Callable

import polars as pl

from src.extract.fetch_countries import fetch_countries
from src.extract.fetch_universities import fetch_universities

logger = logging.getLogger(__name__)

CACHE_DIR = "data/cache"
TTL_SECONDS = 86400


def _path(name: str) -> str:
    return os.path.join(CACHE_DIR, f"{name}.parquet")


def save_cache(df: pl.DataFrame, name: str) -> None:
    if df.is_empty():
        logger.warning("Skipping cache write for empty DataFrame: %s", name)
        return
    os.makedirs(CACHE_DIR, exist_ok=True)
    df.write_parquet(_path(name))


def load_cache(name: str) -> pl.DataFrame | None:
    path = _path(name)
    if not os.path.exists(path):
        return None
    if time.time() - os.path.getmtime(path) >= TTL_SECONDS:
        logger.info("Cache expired for %s", name)
        return None
    try:
        return pl.read_parquet(path)
    except Exception:
        logger.warning("Cache read failed for %s; treating as miss", name)
        return None


def _get(name: str, fetch: Callable[[], pl.DataFrame]) -> pl.DataFrame:
    cached = load_cache(name)
    if cached is not None:
        logger.info("Using cached %s", name)
        return cached
    df = fetch()
    save_cache(df, name)
    return df


def get_countries() -> pl.DataFrame:
    return _get("countries", fetch_countries)


def get_universities() -> pl.DataFrame:
    return _get("universities", fetch_universities)
