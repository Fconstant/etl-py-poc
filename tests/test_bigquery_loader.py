import importlib
from io import BytesIO
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from src.load import bigquery, config


@pytest.fixture(autouse=True)
def reset_modules():
    importlib.reload(config)
    importlib.reload(bigquery)
    yield
    importlib.reload(config)
    importlib.reload(bigquery)


def _df() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "country": ["Brazil"],
            "university_count": [42],
        }
    )


def test_returns_false_when_config_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    result = bigquery.to_bigquery(_df(), "universities_per_country")
    assert result is False


def test_returns_false_and_logs_on_exception(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")
    with patch("src.load.bigquery.bigquery.Client") as mock_client:
        mock_client.side_effect = RuntimeError("network error")
        result = bigquery.to_bigquery(_df(), "universities_per_country")
    assert result is False


def test_returns_true_on_successful_write(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")
    with patch("src.load.bigquery.bigquery.Client") as mock_client:
        mock_load_job = MagicMock()
        mock_client.return_value.load_table_from_file.return_value = mock_load_job
        result = bigquery.to_bigquery(_df(), "universities_per_country")
    assert result is True


def test_parquet_roundtrip():
    df = _df()
    buf = BytesIO()
    df.write_parquet(buf)
    buf.seek(0)
    restored = pl.read_parquet(buf)
    assert restored.shape == df.shape
    assert restored.columns == df.columns
    assert restored["country"].to_list() == ["Brazil"]


def test_schema_keys_match_table_names():
    expected = {
        "universities",
        "universities_per_country",
        "universities_per_continent",
        "top10_universities",
    }
    assert set(bigquery.SCHEMAS.keys()) == expected
