import importlib

import pytest

from src.load import config


@pytest.fixture(autouse=True)
def reset_config():
    importlib.reload(config)
    yield
    importlib.reload(config)


def test_is_ready_when_project_set(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")
    assert config.is_bigquery_ready() is True


def test_is_not_ready_when_project_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    assert config.is_bigquery_ready() is False


def test_default_dataset_id(monkeypatch):
    monkeypatch.delenv("GOOGLE_BIGQUERY_DATASET", raising=False)
    cfg = config.get_bq_config()
    assert cfg.dataset_id == "etl_universities"


def test_custom_dataset_id(monkeypatch):
    monkeypatch.setenv("GOOGLE_BIGQUERY_DATASET", "etl_dev")
    cfg = config.get_bq_config()
    assert cfg.dataset_id == "etl_dev"


def test_project_id_from_env(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLOUD_PROJECT", "my-project")
    cfg = config.get_bq_config()
    assert cfg.project_id == "my-project"


def test_project_id_none_when_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_CLOUD_PROJECT", raising=False)
    cfg = config.get_bq_config()
    assert cfg.project_id is None
