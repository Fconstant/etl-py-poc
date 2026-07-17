import difflib
import logging

import polars as pl

logger = logging.getLogger(__name__)

FUZZY_CUTOFF = 0.8


def normalize_countries(df: pl.DataFrame) -> pl.DataFrame:
    return df.select(["name", "iso_code", "continent", "population", "currency_name"])


def normalize_universities(df: pl.DataFrame, country_names: list[str]) -> pl.DataFrame:
    def _resolve(country: str) -> str | None:
        matches = difflib.get_close_matches(
            country, country_names, n=1, cutoff=FUZZY_CUTOFF
        )
        return matches[0] if matches else None

    resolved = [_resolve(c) for c in df["country"].to_list()]
    unmatched = {
        c for c, r in zip(df["country"].to_list(), resolved, strict=True) if r is None
    }
    if unmatched:
        logger.warning("Unmatched countries: %s", unmatched)

    return df.with_columns(pl.Series("resolved_country", resolved)).filter(
        pl.col("resolved_country").is_not_null()
    )
