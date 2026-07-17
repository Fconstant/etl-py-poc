import typer
from dotenv import load_dotenv

from src.pipeline.run import run as run_pipeline
from src.utils.log import setup_logging

load_dotenv()
app = typer.Typer()


@app.command()
def start() -> None:
    setup_logging()
    run_pipeline()


if __name__ == "__main__":
    app()


def main() -> None:
    app()
