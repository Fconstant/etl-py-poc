import polars as pl


def enrich(df: pl.DataFrame) -> pl.DataFrame:
    return df.select(
        [
            pl.col("name").alias("university_name"),
            pl.col("resolved_country").alias("country"),
            "iso_code",
            "continent",
            "population",
            "currency_name",
        ]
    )
