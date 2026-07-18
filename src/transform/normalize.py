import difflib
import json
import logging
from pathlib import Path

import polars as pl

logger = logging.getLogger(__name__)

FUZZY_CUTOFF = 0.8
ALIASES_PATH = Path("data/country_aliases.json")


def load_country_aliases(path: Path | None = None) -> dict[str, str]:
    with (path or ALIASES_PATH).open(encoding="utf-8") as f:
        data: dict[str, str] = json.load(f)
    return data


def normalize_countries(df: pl.DataFrame) -> pl.DataFrame:
    return df.select(["name", "iso_code", "continent", "population", "currency_name"])


def normalize_universities(
    df: pl.DataFrame, country_names: list[str], aliases: dict[str, str] | None = None
) -> pl.DataFrame:
    if aliases is None:
        aliases = load_country_aliases()
    known = set(country_names)

    def _resolve(country: str) -> str | None:
        if country in known:
            return country
        alias = aliases.get(country)
        if alias is not None and alias in known:
            return alias
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
