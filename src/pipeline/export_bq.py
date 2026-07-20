import polars as pl

from src.load import to_bigquery

OUTPUT_DIR = "data/output"

TABLE_NAMES = [
    "universities",
    "universities_per_country",
    "universities_per_continent",
    "top10_universities",
]


def export_to_bigquery() -> None:
    failed: list[str] = []

    for table_name in TABLE_NAMES:
        path = f"{OUTPUT_DIR}/{table_name}.parquet"
        try:
            df = pl.read_parquet(path)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"{path} not found. Run `etl run` first to generate output files."
            ) from None

        if not to_bigquery(df, table_name):
            failed.append(table_name)

    if failed:
        raise RuntimeError(f"BigQuery export failed for tables: {', '.join(failed)}")

    print(f"BigQuery export complete: {len(TABLE_NAMES)} tables loaded to BigQuery.")
