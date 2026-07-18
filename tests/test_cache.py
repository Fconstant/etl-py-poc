import os
import time

import polars as pl
import pytest

from src.extract import cache


@pytest.fixture(autouse=True)
def cache_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(cache, "CACHE_DIR", str(tmp_path))
    return tmp_path


def _df() -> pl.DataFrame:
    return pl.DataFrame({"name": ["Brazil"]})


def test_hit_within_ttl():
    cache.save_cache(_df(), "countries")
    result = cache.load_cache("countries")
    assert result is not None
    assert result["name"].to_list() == ["Brazil"]


def test_miss_when_absent():
    assert cache.load_cache("countries") is None


def test_miss_when_expired(cache_dir):
    cache.save_cache(_df(), "countries")
    old = time.time() - cache.TTL_SECONDS - 10
    os.utime(cache_dir / "countries.parquet", (old, old))
    assert cache.load_cache("countries") is None


def test_miss_when_corrupted(cache_dir):
    (cache_dir / "countries.parquet").write_text("not parquet")
    assert cache.load_cache("countries") is None


def test_empty_df_not_cached(cache_dir):
    cache.save_cache(pl.DataFrame(), "countries")
    assert not (cache_dir / "countries.parquet").exists()


def test_get_fetches_and_writes_cache(cache_dir, monkeypatch):
    monkeypatch.setattr(cache, "fetch_countries", _df)
    result = cache.get_countries()
    assert result["name"].to_list() == ["Brazil"]
    assert (cache_dir / "countries.parquet").exists()


def test_get_uses_cache_without_fetch(monkeypatch):
    cache.save_cache(_df(), "countries")

    def boom() -> pl.DataFrame:
        raise AssertionError("fetch called despite valid cache")

    monkeypatch.setattr(cache, "fetch_countries", boom)
    assert cache.get_countries()["name"].to_list() == ["Brazil"]
