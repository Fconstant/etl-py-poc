import polars as pl
import pytest
from typer.testing import CliRunner

from src.cli import app
from src.view.report import CSV_NAMES, _df_to_html_table, generate_report


def _cols(*n: str) -> pl.DataFrame:
    return pl.DataFrame({c: [f"v_{c}"] for c in n})


class TestDfToHtmlTable:
    def test_returns_html_with_headers_and_data(self) -> None:
        df = _cols("a", "b")
        html = _df_to_html_table(df, "Test Title")
        assert "<h2>Test Title</h2>" in html
        assert "<th>a" in html
        assert "<th>b" in html
        assert "v_a" in html
        assert "v_b" in html
        assert html.startswith("<section>")
        assert html.endswith("</section>")

    def test_empty_df_shows_no_data(self) -> None:
        df = pl.DataFrame({"x": []})
        html = _df_to_html_table(df, "Empty")
        assert "No data" in html

    def test_empty_df_no_columns_shows_no_data(self) -> None:
        df = pl.DataFrame()
        html = _df_to_html_table(df, "Empty")
        assert "No data" in html


class TestGenerateReport:
    def test_writes_report_html(self, tmp_path: pytest.TempPathFactory) -> None:
        for name in CSV_NAMES:
            _cols("a", "b").write_csv(tmp_path / f"{name}.csv")
        generate_report(str(tmp_path))
        assert (tmp_path / "report.html").exists()
        html = (tmp_path / "report.html").read_text()
        assert "Universities Per Country" in html
        assert "Universities Per Continent" in html
        assert "Top10 Universities" in html
        assert "v_a" in html
        assert "v_b" in html

    def test_raises_on_missing_csv(self, tmp_path: pytest.TempPathFactory) -> None:
        (tmp_path / "universities_per_country.csv").write_text("a,b\n1,2")
        with pytest.raises(FileNotFoundError, match="Missing CSV"):
            generate_report(str(tmp_path))

    def test_empty_csv_shows_no_data(self, tmp_path: pytest.TempPathFactory) -> None:
        for name in CSV_NAMES:
            (tmp_path / f"{name}.csv").write_text("")
        generate_report(str(tmp_path))
        html = (tmp_path / "report.html").read_text()
        assert "No data" in html


class TestCliView:
    def test_view_command_opens_browser(
        self, tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        output_dir = tmp_path / "data" / "output"
        output_dir.mkdir(parents=True)
        for name in CSV_NAMES:
            _cols("x").write_csv(output_dir / f"{name}.csv")
        monkeypatch.chdir(tmp_path)

        calls: list[str] = []

        def fake_open(url: str) -> bool:
            calls.append(url)
            return True

        monkeypatch.setattr("src.cli.webbrowser.open", fake_open)

        runner = CliRunner()
        result = runner.invoke(app, ["view"])
        assert result.exit_code == 0
        assert (output_dir / "report.html").exists()
        assert len(calls) == 1
        assert calls[0] == f"file://{output_dir / 'report.html'}"

    def test_view_command_browser_unavailable(
        self, tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        output_dir = tmp_path / "data" / "output"
        output_dir.mkdir(parents=True)
        for name in CSV_NAMES:
            _cols("x").write_csv(output_dir / f"{name}.csv")
        monkeypatch.chdir(tmp_path)

        def fake_open(url: str) -> bool:
            return False

        monkeypatch.setattr("src.cli.webbrowser.open", fake_open)

        runner = CliRunner()
        result = runner.invoke(app, ["view"])
        assert result.exit_code == 0
        assert (output_dir / "report.html").exists()
        assert "Could not open browser" in result.output
