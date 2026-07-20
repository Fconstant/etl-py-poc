from unittest.mock import patch

import polars as pl

from src.pipeline import run


def _df() -> pl.DataFrame:
    return pl.DataFrame({"country": ["Brazil"], "university_count": [42]})


def _countries_df() -> pl.DataFrame:
    return pl.DataFrame({"name": ["Brazil"]})


def test_run_default_no_bigquery_calls():
    with (
        patch("src.pipeline.run.get_countries", return_value=_df()),
        patch("src.pipeline.run.get_universities", return_value=_df()),
        patch("src.pipeline.run.normalize_countries", return_value=_countries_df()),
        patch("src.pipeline.run.normalize_universities", return_value=_df()),
        patch("src.pipeline.run.join_data", return_value=_df()),
        patch("src.pipeline.run.enrich", return_value=_df()),
        patch("src.pipeline.run.universities_per_country", return_value=_df()),
        patch("src.pipeline.run.universities_per_continent", return_value=_df()),
        patch("src.pipeline.run.top10_countries", return_value=_df()),
        patch("src.pipeline.run.to_csv"),
        patch("src.pipeline.run.to_parquet"),
        patch("src.pipeline.run.to_bigquery") as mock_bq,
    ):
        run.run()

    mock_bq.assert_not_called()


def test_run_with_export_calls_to_bigquery_four_times():
    with (
        patch("src.pipeline.run.get_countries", return_value=_df()),
        patch("src.pipeline.run.get_universities", return_value=_df()),
        patch("src.pipeline.run.normalize_countries", return_value=_countries_df()),
        patch("src.pipeline.run.normalize_universities", return_value=_df()),
        patch("src.pipeline.run.join_data", return_value=_df()),
        patch("src.pipeline.run.enrich", return_value=_df()),
        patch("src.pipeline.run.universities_per_country", return_value=_df()),
        patch("src.pipeline.run.universities_per_continent", return_value=_df()),
        patch("src.pipeline.run.top10_countries", return_value=_df()),
        patch("src.pipeline.run.to_csv"),
        patch("src.pipeline.run.to_parquet"),
        patch("src.pipeline.run.to_bigquery") as mock_bq,
    ):
        run.run(export_bigquery=True)

    assert mock_bq.call_count == 4


def test_run_writes_enriched_table_locally():
    with (
        patch("src.pipeline.run.get_countries", return_value=_df()),
        patch("src.pipeline.run.get_universities", return_value=_df()),
        patch("src.pipeline.run.normalize_countries", return_value=_countries_df()),
        patch("src.pipeline.run.normalize_universities", return_value=_df()),
        patch("src.pipeline.run.join_data", return_value=_df()),
        patch("src.pipeline.run.enrich", return_value=_df()),
        patch("src.pipeline.run.universities_per_country", return_value=_df()),
        patch("src.pipeline.run.universities_per_continent", return_value=_df()),
        patch("src.pipeline.run.top10_countries", return_value=_df()),
        patch("src.pipeline.run.to_csv") as mock_csv,
        patch("src.pipeline.run.to_parquet") as mock_parquet,
        patch("src.pipeline.run.to_bigquery"),
    ):
        run.run()

    names = [call.args[1] for call in mock_csv.call_args_list]
    assert "universities" in names
    parquet_names = [call.args[1] for call in mock_parquet.call_args_list]
    assert "universities" in parquet_names
