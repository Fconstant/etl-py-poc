import os

import polars as pl

OUTPUT_DIR = "data/output"


def _ensure_dir() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def to_csv(df: pl.DataFrame, name: str) -> None:
    _ensure_dir()
    df.write_csv(os.path.join(OUTPUT_DIR, f"{name}.csv"))


def to_parquet(df: pl.DataFrame, name: str) -> None:
    _ensure_dir()
    df.write_parquet(os.path.join(OUTPUT_DIR, f"{name}.parquet"))
