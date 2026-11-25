"""Export the cleaned spells table as JSON for the website.

Run with `uv run python -m manager_tenure.export` (or `make data`).

The website is written in JavaScript, which reads JSON rather than parquet.
JSON has no date type, so dates are written as plain text ("2019-12-22").
Missing values become null. Everything else is copied across unchanged.
"""

import json
from pathlib import Path

from loguru import logger
import pandas as pd

from manager_tenure.config import SPELLS_FILE, SPELLS_JSON_FILE

DATE_COLUMNS = ["start_date", "end_date", "pl_start_date", "snapshot_date"]


def to_web_records(spells: pd.DataFrame) -> list[dict]:
    """Turn the spells table into a list of plain dictionaries, one per spell.

    Date columns become "YYYY-MM-DD" text. Columns that aren't present are skipped,
    so this still works if the table changes shape.
    """
    table = spells.copy()
    for column in DATE_COLUMNS:
        if column in table.columns:
            table[column] = table[column].dt.strftime("%Y-%m-%d")
    # where() turns missing values (NaN, NaT) into None, which JSON writes as null.
    table = table.astype(object).where(table.notna(), None)
    return table.to_dict(orient="records")


def write_spells_json(spells: pd.DataFrame, output_path: Path) -> None:
    """Write the spells as a JSON array to output_path."""
    records = to_web_records(spells)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
    logger.success(f"Wrote {len(records)} spells to {output_path}")


def main(input_path: Path = SPELLS_FILE, output_path: Path = SPELLS_JSON_FILE) -> None:
    """Read the cleaned parquet file and write the JSON for the website."""
    spells = pd.read_parquet(input_path)
    write_spells_json(spells, output_path)


if __name__ == "__main__":
    main()
