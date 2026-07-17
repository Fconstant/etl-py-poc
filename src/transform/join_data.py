import polars as pl


def join_data(universities: pl.DataFrame, countries: pl.DataFrame) -> pl.DataFrame:
    return universities.join(
        countries,
        left_on="resolved_country",
        right_on="name",
        how="inner",
    )
