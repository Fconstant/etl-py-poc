import polars as pl


def universities_per_country(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("country")
        .len(name="university_count")
        .sort("university_count", descending=True)
    )


def universities_per_continent(df: pl.DataFrame) -> pl.DataFrame:
    return (
        df.group_by("continent")
        .len(name="university_count")
        .sort("university_count", descending=True)
    )


def top10_countries(df: pl.DataFrame) -> pl.DataFrame:
    return universities_per_country(df).head(10)
