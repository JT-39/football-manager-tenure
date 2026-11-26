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

from manager_tenure.config import PREMIER_LEAGUE_SEASONS_FILE, RAW_DATA_DIR, SPELLS_FILE
from manager_tenure.dataset import find_latest_snapshot, metadata_path
from manager_tenure.premier_league import league_periods
from manager_tenure.schema import SPELLS_SCHEMA

# The symbols Wikipedia puts after a manager's name (see the key at the top of
# the page): † current manager, ‡ caretaker, § current but club relegated.
CARETAKER_MARKER = "‡"
NAME_MARKERS = "†‡§"

# Columns that tidy_columns needs to find in the Wikipedia table.
TABLE_COLUMNS_TO_TIDY = [
    "Name",
    "Club",
    "From",
    "Until",
    "Duration (days)",
    "Nat.",
    "Years in League",
    "Ref.",
]


def read_spells_table(html_path: Path) -> pd.DataFrame:
    """Read the table of managerial spells from the saved Wikipedia page.

    The page has about ten tables; the spells table is the only one with a
    "Duration (days)" column.
    """

    tables = pd.read_html(html_path, match="Duration")
    # Fail loudly if Wikipedia adds a second table with "Duration" in it, rather
    # than silently reading the first one.
    if len(tables) != 1:
        raise ValueError(f"Expected one spells table, found {len(tables)} with 'Duration'.")
    return tables[0]


def tidy_columns(spells: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to snake_case and drop the ones we don't use.

    Keeps: name, club, from, until, duration_days, and nationality (added by
    main() from the flag images before this step runs).
    Drops: "Nat." (empty, pandas can't read flag images), "Years in League"
    (Wikipedia's season labels, which are not reliable enough: Premier League
    time now comes from match data, see premier_league.py), and "Ref." (citation
    numbers).
    """
    missing = [col for col in TABLE_COLUMNS_TO_TIDY if col not in spells.columns]
    if missing:
        raise KeyError(f"Wikipedia table is missing expected columns: {missing}")

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


def premier_league_days(
    start: pd.Timestamp, end: pd.Timestamp, seasons: list[tuple[pd.Timestamp, pd.Timestamp]]
) -> int:
    """Count the days of a spell (start to end) that fall inside the Premier League seasons."""
    days = 0
    for season_start, season_end in seasons:
        overlap_start = max(start, season_start)
        overlap_end = min(end, season_end)
        if overlap_end > overlap_start:
            days += (overlap_end - overlap_start).days
    return days


def add_tenure(spells: pd.DataFrame, memberships: pd.DataFrame) -> pd.DataFrame:
    """Add two measures of how long each spell lasted, in days.

    - tenure_days: total time in charge, from start_date to end_date, including
      any time before the Premier League existed or while the club was in a
      lower division.
    - pl_tenure_days: only the days that fall in the club's Premier League
      seasons, from the match-based membership table (premier_league.py). This is
      the number to use when comparing managers across eras.
    """
    spells = spells.copy()
    # Subtracting two dates gives a duration; .dt.days turns it into whole days.
    spells["tenure_days"] = (spells["end_date"] - spells["start_date"]).dt.days
    periods = league_periods(memberships)
    spells["pl_tenure_days"] = [
        premier_league_days_for_spell(row.club, row.start_date, row.end_date, periods)
        for row in spells.itertuples()
    ]
    return spells


def premier_league_days_for_spell(
    club: str, start: pd.Timestamp, end: pd.Timestamp, memberships: pd.DataFrame
) -> int:
    """Count the days of one spell that fall in the club's Premier League seasons."""
    club_seasons = memberships[memberships["club"] == club]
    seasons = list(zip(club_seasons["start_date"], club_seasons["end_date"], strict=True))
    return premier_league_days(start, end, seasons)


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
        cells = row.findall("td")
        flags = cells[0].findall(".//img") if cells else []
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
    nationalities = read_nationalities(html_path)
    # The names come from pandas and the flags from lxml, so check they line up.
    # If they don't, a nationality would silently attach to the wrong manager.
    if len(nationalities) != len(spells):
        raise ValueError(
            f"Found {len(spells)} spell rows but {len(nationalities)} flag rows. They must match."
        )
    spells["nationality"] = nationalities
    spells = (
        spells.pipe(tidy_columns)
        .pipe(flag_caretakers)
        .pipe(parse_dates, as_of=snapshot_date(html_path))
        .pipe(add_tenure, memberships=pd.read_parquet(PREMIER_LEAGUE_SEASONS_FILE))
    )
    spells["snapshot_date"] = pd.Timestamp(snapshot_date(html_path))

    SPELLS_SCHEMA.validate(spells)  # raises a clear error if any rule is broken
    output_path.parent.mkdir(parents=True, exist_ok=True)
    spells.to_parquet(output_path, index=False)
    logger.success(f"Saved {len(spells)} spells to {output_path}")


if __name__ == "__main__":
    main()
