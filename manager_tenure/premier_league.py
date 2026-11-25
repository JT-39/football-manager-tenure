"""Work out which clubs were in the Premier League, and on which dates, each season.

Source: football-data.co.uk, which publishes one CSV file per season listing every
match. A club's first and last match in a season give the dates it was in the
league that season. The 1992–93 season has no file, so its clubs are entered by
hand in clubs.py.

Run with `uv run python -m manager_tenure.premier_league` (or `make data`).
Add `--refresh` to download the season files again, even if they exist.

The downloads are saved unchanged in data/raw/football_data/ with a manifest.json
recording the address, the download time and a checksum for each file.
"""

import csv
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import sys

from loguru import logger
import pandas as pd
import requests

from manager_tenure.clubs import FOOTBALL_DATA_TO_WIKIPEDIA, FOUNDING_CLUBS_1992
from manager_tenure.config import (
    FIRST_PL_SEASON,
    FOOTBALL_DATA_BASE_URL,
    FOOTBALL_DATA_DIR,
    LAST_PL_SEASON,
    PREMIER_LEAGUE_SEASONS_FILE,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)

MANIFEST_NAME = "manifest.json"
# The 1992–93 season, as approximate dates: the first matches and the last day.
FOUNDING_START = pd.Timestamp("1992-08-15")
FOUNDING_END = pd.Timestamp("1993-05-11")


def season_code(start_year: int) -> str:
    """Return the football-data code for a season, e.g. 2025 -> "2526"."""
    return f"{start_year % 100:02d}{(start_year + 1) % 100:02d}"


def season_file(raw_dir: Path, start_year: int) -> Path:
    """Return where a season's CSV file is saved, e.g. raw/football_data/E0_2526.csv."""
    return raw_dir / f"E0_{season_code(start_year)}.csv"


def download_seasons(raw_dir: Path = FOOTBALL_DATA_DIR, refresh: bool = False) -> None:
    """Download each season's CSV file that isn't already saved, then update the manifest."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = raw_dir / MANIFEST_NAME
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}

    for start_year in range(FIRST_PL_SEASON, LAST_PL_SEASON + 1):
        path = season_file(raw_dir, start_year)
        if path.exists() and not refresh:
            continue
        url = f"{FOOTBALL_DATA_BASE_URL}/{season_code(start_year)}/E0.csv"
        response = requests.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        path.write_bytes(response.content)
        manifest[path.name] = {
            "url": url,
            "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "sha256": hashlib.sha256(response.content).hexdigest(),
            "bytes": len(response.content),
        }
        logger.info(f"Downloaded {path.name}")

    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def read_matches(path: Path) -> pd.DataFrame:
    """Read the date and the two teams from every match in a season file.

    The older files have rows with a different number of columns from the header,
    and a plain CSV reader drops those rows, losing real matches. So this reads each
    row by position and only skips rows that are blank or too short.
    """
    with path.open(encoding="latin1") as file:
        rows = list(csv.reader(file))
    header = rows[0]
    date_col, home_col, away_col = (
        header.index(name) for name in ("Date", "HomeTeam", "AwayTeam")
    )
    needed = max(date_col, home_col, away_col)

    matches = [
        (row[date_col], row[home_col].strip(), row[away_col].strip())
        for row in rows[1:]
        if len(row) > needed and row[home_col].strip()
    ]
    table = pd.DataFrame(matches, columns=["date", "home", "away"])
    table["date"] = pd.to_datetime(table["date"], dayfirst=True, format="mixed")
    return table


def season_memberships(path: Path, start_year: int) -> pd.DataFrame:
    """Return each club's first and last match date in one season file.

    The end date is the day after the last match, so the interval is half-open:
    a spell that ends on the last match day counts that day as Premier League time.
    """
    matches = read_matches(path)
    teams = pd.concat(
        [
            matches[["date", "home"]].rename(columns={"home": "team"}),
            matches[["date", "away"]].rename(columns={"away": "team"}),
        ]
    )

    unknown = sorted(set(teams["team"]) - set(FOOTBALL_DATA_TO_WIKIPEDIA))
    if unknown:
        raise KeyError(f"Unknown club names in {path.name}: {unknown}. Add them to clubs.py.")
    teams["club"] = teams["team"].map(FOOTBALL_DATA_TO_WIKIPEDIA)

    seasons = teams.groupby("club").agg(start_date=("date", "min"), last_match=("date", "max"))
    seasons["end_date"] = seasons["last_match"] + pd.Timedelta(days=1)
    seasons = seasons.drop(columns="last_match").reset_index()
    seasons["season"] = start_year
    return seasons[["club", "season", "start_date", "end_date"]]


def founding_memberships() -> pd.DataFrame:
    """Return the 1992–93 clubs, with approximate dates for that season."""
    return pd.DataFrame(
        {
            "club": FOUNDING_CLUBS_1992,
            "season": 1992,
            "start_date": FOUNDING_START,
            "end_date": FOUNDING_END,
        }
    )


def build_memberships(raw_dir: Path = FOOTBALL_DATA_DIR) -> pd.DataFrame:
    """Combine the 1992–93 clubs with every season file into one table."""
    tables = [founding_memberships()]
    for start_year in range(FIRST_PL_SEASON, LAST_PL_SEASON + 1):
        tables.append(season_memberships(season_file(raw_dir, start_year), start_year))
    memberships = pd.concat(tables, ignore_index=True)
    return memberships.sort_values(["club", "start_date"]).reset_index(drop=True)


def league_periods(memberships: pd.DataFrame) -> pd.DataFrame:
    """Join each club's seasons into unbroken Premier League periods.

    A summer break counts as Premier League time when the club is in the league
    both before and after it, so a manager who stays through the summer keeps
    being charged with those days. A club that is promoted or relegated does not
    get the summer it spent outside the league, because that summer falls between
    two separate periods.

    A period runs from the start of the first season in an unbroken run of
    seasons to the end of the last one. The run's summers are inside it.
    """
    periods = []
    for club, seasons in memberships.sort_values(["club", "season"]).groupby("club"):
        run_start = None
        previous = None
        for row in seasons.itertuples():
            if previous is None or row.season != previous.season + 1:
                if previous is not None:
                    periods.append((club, run_start, previous.end_date))
                run_start = row.start_date
            previous = row
        periods.append((club, run_start, previous.end_date))
    return pd.DataFrame(periods, columns=["club", "start_date", "end_date"])


def main(refresh: bool = False) -> None:
    """Download any missing season files, then save the membership table."""
    download_seasons(refresh=refresh)
    memberships = build_memberships()
    PREMIER_LEAGUE_SEASONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    memberships.to_parquet(PREMIER_LEAGUE_SEASONS_FILE, index=False)
    logger.success(f"Saved {len(memberships)} club-seasons to {PREMIER_LEAGUE_SEASONS_FILE}")


if __name__ == "__main__":
    main(refresh="--refresh" in sys.argv)
