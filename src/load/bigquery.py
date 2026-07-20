import logging
from io import BytesIO

import polars as pl
from google.api_core.exceptions import NotFound
from google.cloud import bigquery
from google.cloud.bigquery import LoadJobConfig, SchemaField, WriteDisposition

from src.load.config import get_bq_config, is_bigquery_ready

logger = logging.getLogger(__name__)

SCHEMAS: dict[str, list[SchemaField]] = {
    "universities": [
        SchemaField("university_name", "STRING"),
        SchemaField("country", "STRING"),
        SchemaField("iso_code", "STRING"),
        SchemaField("continent", "STRING"),
        SchemaField("population", "INT64"),
        SchemaField("currency_name", "STRING"),
    ],
    "universities_per_country": [
        SchemaField("country", "STRING"),
        SchemaField("university_count", "INT64"),
    ],
    "universities_per_continent": [
        SchemaField("continent", "STRING"),
        SchemaField("university_count", "INT64"),
    ],
    "top10_universities": [
        SchemaField("country", "STRING"),
        SchemaField("university_count", "INT64"),
    ],
}


_client_instance: bigquery.Client | None = None


def _get_client() -> bigquery.Client:
    global _client_instance
    if _client_instance is None:
        _client_instance = bigquery.Client(project=get_bq_config().project_id)
    return _client_instance


def _get_or_create_dataset(client: bigquery.Client, dataset_id: str) -> None:
    full_id = f"{client.project}.{dataset_id}"
    dataset = bigquery.Dataset(full_id)
    dataset.location = "US"
    try:
        client.get_dataset(full_id)
    except NotFound:
        client.create_dataset(dataset, exists_ok=True)
        logger.info("Created dataset %s", dataset_id)


def _get_or_create_table(
    client: bigquery.Client,
    dataset_id: str,
    table_id: str,
    schema: list[SchemaField],
) -> None:
    table_ref = bigquery.Table(
        f"{client.project}.{dataset_id}.{table_id}", schema=schema
    )
    try:
        client.get_table(table_ref)
    except NotFound:
        client.create_table(table_ref)
        logger.info("Created table %s.%s", dataset_id, table_id)


def to_bigquery(df: pl.DataFrame, table_name: str) -> bool:
    if not is_bigquery_ready():
        return False
    try:
        config = get_bq_config()
        client = _get_client()

        schema = SCHEMAS[table_name]
        _get_or_create_dataset(client, config.dataset_id)
        _get_or_create_table(client, config.dataset_id, table_name, schema)

        buf = BytesIO()
        df.write_parquet(buf)
        buf.seek(0)

        table_ref = f"{config.project_id}.{config.dataset_id}.{table_name}"
        job_config = LoadJobConfig(
            source_format=bigquery.SourceFormat.PARQUET,
            write_disposition=WriteDisposition.WRITE_TRUNCATE,
        )
        job = client.load_table_from_file(buf, table_ref, job_config=job_config)
        job.result()
        logger.info("Loaded %s → %s (%d rows)", table_name, table_ref, len(df))
        return True
    except Exception:
        logger.warning("BigQuery write failed for table %s", table_name, exc_info=True)
        return False
