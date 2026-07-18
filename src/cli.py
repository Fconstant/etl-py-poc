import typer
from dotenv import load_dotenv

from src.extract.cache import save_cache
from src.extract.fetch_countries import fetch_countries
from src.extract.fetch_universities import fetch_universities
from src.pipeline.run import run as run_pipeline
from src.utils.log import setup_logging

load_dotenv()
app = typer.Typer()


@app.command()
def extract() -> None:
    setup_logging()
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
    setup_logging()
    run_pipeline()


if __name__ == "__main__":
    app()


def main() -> None:
    app()
