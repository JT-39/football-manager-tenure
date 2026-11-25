"""Clean the raw Wikipedia snapshot into a tidy table: one row per managerial spell.

Run with `uv run python -m manager_tenure.features` (or `make data`).

The steps run in order, each taking a DataFrame and returning a new one:

    read_spells_table      raw HTML     -> the spells table as pandas reads it
    read_nationalities     + nationality, read from the flag images
    tidy_columns           snake_case names, drop columns we don't need
    flag_caretakers        is_caretaker column, markers removed from names
    parse_dates            real dates, plus is_ongoing for current spells
    add_tenure             tenure in days: full spell and Premier League only

Each function has tests in tests/test_features.py. Hints for each step are in
docs/docs/milestone-1b-exercises.md.
"""

from datetime import date
import json
from pathlib import Path

# Importing janitor adds the .clean_names() method to DataFrames (used in tidy_columns).
import janitor  # noqa: F401
from loguru import logger
from lxml import html
import pandas as pd

from manager_tenure.config import PREMIER_LEAGUE_START, RAW_DATA_DIR, SPELLS_FILE
from manager_tenure.dataset import find_latest_snapshot, metadata_path

# The symbols Wikipedia puts after a manager's name (see the key at the top of
# the page): † current manager, ‡ caretaker, § current but club relegated.
CARETAKER_MARKER = "‡"
NAME_MARKERS = "†‡§"


def read_spells_table(html_path: Path) -> pd.DataFrame:
    """Read the table of managerial spells from the saved Wikipedia page.

    The page has about ten tables; the spells table is the only one with a
    "Duration (days)" column.
    """

    spells = pd.read_html(html_path, match="Duration")[0]

    return spells


def tidy_columns(spells: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to snake_case and drop the ones we don't use.

    Keeps: name, nationality (if present), club, from, until, duration_days.
    Drops: "Nat." (empty, pandas can't read flag images), "Years in League"
    (we compute our own), "Ref." (citation numbers).
    """

    spells = spells.drop(columns=["Nat.", "Years in League", "Ref."])
    spells = spells.clean_names(strip_underscores=True)

    return spells


def flag_caretakers(spells: pd.DataFrame) -> pd.DataFrame:
    """Add is_caretaker (True if the name has ‡) and strip all markers from names.

    "Stewart Houston ‡" becomes "Stewart Houston" with is_caretaker=True.
    "Mikel Arteta †" becomes "Mikel Arteta" with is_caretaker=False.
    """
    spells = spells.copy()  # work on a copy so the caller's table is not changed
    spells["is_caretaker"] = spells["name"].str.contains(CARETAKER_MARKER, regex=False)
    # strip() removes characters from the start and end of each name only.
    spells["name"] = spells["name"].str.strip(NAME_MARKERS + " ")
    return spells


def parse_dates(spells: pd.DataFrame, as_of: date) -> pd.DataFrame:
    """Turn the text dates into real dates.

    Adds start_date, end_date and is_ongoing. Ongoing spells show "Present*"
    on Wikipedia; their end_date is set to as_of (the day the snapshot was
    taken) so their tenure so far can be measured. The original text columns
    "from" and "until" are dropped.
    """
    spells = spells.copy()
    # Ongoing spells say "Present*" on Wikipedia, rather than a date.
    spells["is_ongoing"] = spells["until"].str.startswith("Present")

    # Remove footnote markers such as "[a]" (a regular expression: \[ is a
    # literal "[", and .*? matches the letters up to the next "]").
    from_text = spells["from"].str.replace(r"\[.*?\]", "", regex=True)
    until_text = spells["until"].str.replace(r"\[.*?\]", "", regex=True)

    spells["start_date"] = pd.to_datetime(from_text, format="%d %B %Y")
    # Blank out the ongoing rows first, so they become missing dates (NaT).
    end_dates = pd.to_datetime(until_text.where(~spells["is_ongoing"]), format="%d %B %Y")
    # Ongoing spells run up to the day the snapshot was taken.
    spells["end_date"] = end_dates.fillna(pd.Timestamp(as_of))

    return spells.drop(columns=["from", "until"])


def add_tenure(spells: pd.DataFrame, league_start: str = PREMIER_LEAGUE_START) -> pd.DataFrame:
    """Add how long each spell lasted, in days, two ways.

    - tenure_days: the full spell, from start_date to end_date.
    - pl_start_date / pl_tenure_days: only the Premier League part. Spells that
      began before league_start count from league_start instead.
    """
    spells = spells.copy()
    # Subtracting two dates gives a duration; .dt.days turns it into whole days.
    spells["tenure_days"] = (spells["end_date"] - spells["start_date"]).dt.days
    # clip() keeps each date no earlier than the league start, so spells that
    # began before 1992 only count from August 1992.
    spells["pl_start_date"] = spells["start_date"].clip(lower=pd.Timestamp(league_start))
    spells["pl_tenure_days"] = (spells["end_date"] - spells["pl_start_date"]).dt.days
    return spells


def read_nationalities(html_path: Path) -> list[str]:
    """Return each spell's nationality, in table order, from the flag images.

    pandas can't read images, but each flag is an <img> whose alt text is the
    country name, e.g. alt="Scotland".
    """
    # pandas cannot see images, so read the HTML directly with lxml.
    doc = html.parse(str(html_path))
    # The spells table is the one whose text contains "Duration".
    table = next(t for t in doc.iter("table") if "Duration" in t.text_content())

    nationalities = []
    # The first row is the header, so skip it.
    for row in table.findall(".//tr")[1:]:
        # The first <td> in each row holds the flag. Its <img alt="..."> gives
        # the country name; a row with no flag gets None.
        flags = row.findall("td")[0].findall(".//img")
        nationalities.append(flags[0].get("alt") if flags else None)
    return nationalities


def snapshot_date(html_path: Path) -> date:
    """Return the day a snapshot was downloaded, from its metadata file."""
    metadata = json.loads(metadata_path(html_path).read_text())
    return date.fromisoformat(metadata["retrieved_at"][:10])


def main(raw_dir: Path = RAW_DATA_DIR, output_path: Path = SPELLS_FILE) -> None:
    """Clean the newest raw snapshot and save the result as a parquet file."""
    html_path = find_latest_snapshot(raw_dir)
    if html_path is None:
        raise FileNotFoundError(f"No snapshot in {raw_dir}. Run `make data` first.")
    logger.info(f"Cleaning {html_path.name}")

    spells = read_spells_table(html_path)
    spells["nationality"] = read_nationalities(html_path)
    spells = (
        spells.pipe(tidy_columns)
        .pipe(flag_caretakers)
        .pipe(parse_dates, as_of=snapshot_date(html_path))
        .pipe(add_tenure)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    spells.to_parquet(output_path, index=False)
    logger.success(f"Saved {len(spells)} spells to {output_path}")


if __name__ == "__main__":
    main()
