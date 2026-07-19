import pathlib

import polars as pl
from tabulate import tabulate

CSV_NAMES: list[str] = [
    "universities_per_country",
    "universities_per_continent",
    "top10_universities",
]


def _df_to_html_table(df: pl.DataFrame, title: str) -> str:
    if df.is_empty():
        if df.columns:
            cols = "".join(f"<th>{c}</th>" for c in df.columns)
            table_html = (
                f"<table>\n<thead>\n<tr>{cols}</tr>\n</thead>\n<tbody>\n"
                f"<tr><td colspan='{len(df.columns)}' "
                f"style='text-align: center; font-style: italic;'>"
                f"No data</td></tr>\n</tbody>\n</table>"
            )
        else:
            table_html = (
                "<table>\n"
                "<thead>\n<tr><th>No data</th></tr>\n</thead>\n"
                "<tbody>\n<tr><td style='text-align: center; font-style: italic;'>"
                "No data</td></tr>\n</tbody>\n</table>"
            )
    else:
        table_html = tabulate(df.rows(), headers=df.columns, tablefmt="html")
    return f"<section>\n<h2>{title}</h2>\n{table_html}\n</section>"


def generate_report(output_dir: str = "data/output") -> None:
    out = pathlib.Path(output_dir)
    sections: list[str] = []
    for name in CSV_NAMES:
        path = out / f"{name}.csv"
        if not path.exists():
            raise FileNotFoundError(f"Missing CSV: {path}")
        df = pl.read_csv(path) if path.stat().st_size > 0 else pl.DataFrame()
        title = name.replace("_", " ").title()
        sections.append(_df_to_html_table(df, title))
    html = (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        "<title>ETL Pipeline Report</title>\n"
        "<style>\n"
        "  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', "
        "Roboto, sans-serif; margin: 2rem; background: #fafafa; }\n"
        "  h1 { color: #222; }\n"
        "  h2 { color: #333; margin-top: 1.5rem; }\n"
        "  table { border-collapse: collapse; width: 100%; "
        "margin-bottom: 2rem; background: #fff; }\n"
        "  th { background-color: #4a90d9; color: white; font-weight: bold; "
        "padding: 0.75rem; text-align: left; border: 1px solid #357abd; }\n"
        "  td { padding: 0.5rem 0.75rem; border: 1px solid #ddd; }\n"
        "  tr:nth-child(even) td { background-color: #f5f5f5; }\n"
        "  tr:hover td { background-color: #e8f0fe; }\n"
        "  section { margin-bottom: 2rem; }\n"
        "</style>\n"
        "</head>\n"
        "<body>\n"
        "<h1>ETL Pipeline Report</h1>\n"
        f"{chr(10).join(sections)}\n"
        "</body>\n"
        "</html>"
    )
    (out / "report.html").write_text(html)
