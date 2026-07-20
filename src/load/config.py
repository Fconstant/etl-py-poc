import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class BigQueryConfig:
    project_id: str | None
    dataset_id: str


_config: BigQueryConfig | None = None
_warning_logged: bool = False


def _build_config() -> BigQueryConfig:
    return BigQueryConfig(
        project_id=os.environ.get("GOOGLE_CLOUD_PROJECT") or None,
        dataset_id=os.environ.get("GOOGLE_BIGQUERY_DATASET", "etl_universities"),
    )


def get_bq_config() -> BigQueryConfig:
    global _config
    if _config is None:
        _config = _build_config()
    return _config


def is_bigquery_ready() -> bool:
    global _warning_logged
    config = get_bq_config()
    if config.project_id:
        return True
    if not _warning_logged:
        logger.warning(
            "GOOGLE_CLOUD_PROJECT environment variable is not set. "
            "BigQuery operations will be skipped. "
            "Set it or use --export-bigquery with valid credentials."
        )
        _warning_logged = True
    return False
