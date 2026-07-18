from src.extract.cache import get_countries, get_universities
from src.load.loader import to_csv, to_parquet
from src.transform.aggregate import (
    top10_countries,
    universities_per_continent,
    universities_per_country,
)
from src.transform.enrich import enrich
from src.transform.join_data import join_data
from src.transform.normalize import normalize_countries, normalize_universities


def run() -> None:
    countries_raw = get_countries()
    universities_raw = get_universities()

    countries = normalize_countries(countries_raw)
    country_names = countries["name"].to_list()
    universities = normalize_universities(universities_raw, country_names)

    joined = join_data(universities, countries)
    enriched = enrich(joined)

    by_country = universities_per_country(enriched)
    by_continent = universities_per_continent(enriched)
    top10 = top10_countries(enriched)

    for df, name in [
        (by_country, "universities_per_country"),
        (by_continent, "universities_per_continent"),
        (top10, "top10_universities"),
    ]:
        to_csv(df, name)
        to_parquet(df, name)

    print(
        f"Pipeline complete: {len(countries_raw)} countries, "
        f"{len(universities_raw)} universities processed."
    )
