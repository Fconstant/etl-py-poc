import pathlib
import webbrowser

import typer
from dotenv import load_dotenv

from src.extract.cache import save_cache
from src.extract.fetch_countries import fetch_countries
from src.extract.fetch_universities import fetch_universities
from src.pipeline.run import run as run_pipeline
from src.utils.log import setup_logging
from src.view.report import generate_report

load_dotenv()
setup_logging()
app = typer.Typer()


@app.command()
def extract() -> None:
    countries = fetch_countries()
    save_cache(countries, "countries")
    universities = fetch_universities()
    save_cache(universities, "universities")
    print(
        f"Extraction complete: {len(countries)} countries, "
        f"{len(universities)} universities cached in data/cache/."
    )


@app.command()
def run() -> None:
    run_pipeline()


@app.command()
def view() -> None:
    generate_report()
    report_path = pathlib.Path("data/output/report.html").resolve()
    uri = f"file://{report_path}"
    if webbrowser.open(uri):
        print(f"Report opened in browser: {report_path}")
    else:
        print(f"Report generated: {report_path}")
        print("(Could not open browser — open the file manually)")


if __name__ == "__main__":
    app()


def main() -> None:
    app()
