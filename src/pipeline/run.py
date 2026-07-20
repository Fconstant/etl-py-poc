from src.extract.cache import get_countries, get_universities
from src.load import to_bigquery, to_csv, to_parquet
from src.transform.aggregate import (
    top10_countries,
    universities_per_continent,
    universities_per_country,
)
from src.transform.enrich import enrich
from src.transform.join_data import join_data
from src.transform.normalize import normalize_countries, normalize_universities


def run(export_bigquery: bool = False) -> None:
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

    bq_success: list[str] = []
    bq_failed: list[str] = []
    for df, name in [
        (enriched, "universities"),
        (by_country, "universities_per_country"),
        (by_continent, "universities_per_continent"),
        (top10, "top10_universities"),
    ]:
        to_csv(df, name)
        to_parquet(df, name)
        if export_bigquery:
            if to_bigquery(df, name):
                bq_success.append(name)
            else:
                bq_failed.append(name)

    print(
        f"Pipeline complete: {len(countries_raw)} countries, "
        f"{len(universities_raw)} universities processed."
    )
    if export_bigquery:
        print(f"BigQuery: {len(bq_success)} tables loaded, {len(bq_failed)} failed")
