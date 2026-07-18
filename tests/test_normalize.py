import polars as pl

from src.transform.normalize import load_country_aliases, normalize_universities


def _unis(*countries: str) -> pl.DataFrame:
    return pl.DataFrame(
        {"name": [f"Uni {c}" for c in countries], "country": list(countries)}
    )


def test_alias_hit():
    df = normalize_universities(
        _unis("Russian Federation"),
        ["Russia", "Brazil"],
        {"Russian Federation": "Russia"},
    )
    assert df["resolved_country"].to_list() == ["Russia"]


def test_fuzzy_fallback_still_works():
    df = normalize_universities(
        _unis("Turkiye"),
        ["Türkiye", "Brazil"],
        {},
    )
    assert df["resolved_country"].to_list() == ["Türkiye"]


def test_drc_approximate_alias():
    df = normalize_universities(
        _unis("Congo, the Democratic Republic of the"),
        ["Congo", "Brazil"],
        load_country_aliases(),
    )
    assert df["resolved_country"].to_list() == ["Congo"]


def test_alias_target_absent_falls_through():
    df = normalize_universities(
        _unis("Russian Federation"),
        ["Brazil"],
        {"Russian Federation": "Russia"},
    )
    assert df.is_empty()


def test_default_load_uses_shipped_aliases():
    df = normalize_universities(_unis("Swaziland"), ["Eswatini", "Brazil"])
    assert df["resolved_country"].to_list() == ["Eswatini"]


def test_explicit_aliases_skip_file_read(monkeypatch, tmp_path):
    from src.transform import normalize

    monkeypatch.setattr(normalize, "ALIASES_PATH", tmp_path / "missing.json")
    df = normalize_universities(_unis("Brazil"), ["Brazil"], {})
    assert df["resolved_country"].to_list() == ["Brazil"]


def test_load_country_aliases_reads_shipped_json():
    aliases = load_country_aliases()
    assert aliases["Russian Federation"] == "Russia"
    assert aliases["Swaziland"] == "Eswatini"
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in aliases.items())
