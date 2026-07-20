from unittest.mock import patch

import polars as pl
import pytest

from src.pipeline import export_bq


def _df() -> pl.DataFrame:
    return pl.DataFrame({"country": ["Brazil"], "university_count": [42]})


def test_raises_when_parquet_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(export_bq, "OUTPUT_DIR", str(tmp_path))
    with pytest.raises(FileNotFoundError, match="not found"):
        export_bq.export_to_bigquery()


def test_raises_runtime_error_when_to_bigquery_returns_false(tmp_path, monkeypatch):
    monkeypatch.setattr(export_bq, "OUTPUT_DIR", str(tmp_path))
    for name in export_bq.TABLE_NAMES:
        _df().write_parquet(f"{tmp_path}/{name}.parquet")

    with (
        patch("src.pipeline.export_bq.to_bigquery", return_value=False),
        pytest.raises(RuntimeError, match="BigQuery export failed"),
    ):
        export_bq.export_to_bigquery()


def test_completes_when_all_writes_succeed(tmp_path, monkeypatch):
    monkeypatch.setattr(export_bq, "OUTPUT_DIR", str(tmp_path))
    for name in export_bq.TABLE_NAMES:
        _df().write_parquet(f"{tmp_path}/{name}.parquet")

    with patch("src.pipeline.export_bq.to_bigquery", return_value=True) as mock_bq:
        export_bq.export_to_bigquery()

    assert mock_bq.call_count == len(export_bq.TABLE_NAMES)


def test_calls_to_bigquery_for_each_table(tmp_path, monkeypatch):
    monkeypatch.setattr(export_bq, "OUTPUT_DIR", str(tmp_path))
    for name in export_bq.TABLE_NAMES:
        _df().write_parquet(f"{tmp_path}/{name}.parquet")

    with patch("src.pipeline.export_bq.to_bigquery", return_value=True) as mock_bq:
        export_bq.export_to_bigquery()

    called_names = [call.args[1] for call in mock_bq.call_args_list]
    assert called_names == export_bq.TABLE_NAMES
