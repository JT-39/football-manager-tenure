"""Match results for each manager's spell: points, goals and points per game.

Every Premier League match in the football-data.co.uk season files is given to
the manager who was in charge of that club on that day. Then each spell gets
its totals: matches, points, points per game and goal difference per game.

Run with `uv run python -m manager_tenure.results` (or `make data`).

Two outputs:
- spell_matches.parquet: one row per club per match, with the spell it belongs to.
- spell_results.parquet: one row per spell, with its totals.
"""

from pathlib import Path

from loguru import logger
import pandas as pd

from manager_tenure.clubs import FOOTBALL_DATA_TO_WIKIPEDIA
from manager_tenure.config import (
    FIRST_PL_SEASON,
    FOOTBALL_DATA_DIR,
    LAST_PL_SEASON,
    SPELL_MATCHES_FILE,
    SPELL_RESULTS_FILE,
    SPELLS_FILE,
)
from manager_tenure.premier_league import read_columns, season_file
from manager_tenure.schema import SPELL_MATCHES_SCHEMA, SPELL_RESULTS_SCHEMA

RESULT_COLUMNS = ["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]


def points_for(goals_for: int, goals_against: int) -> int:
    """Three points for a win, one for a draw, none for a loss."""
    if goals_for > goals_against:
        return 3
    if goals_for == goals_against:
        return 1
    return 0


def read_season_results(path: Path, start_year: int) -> pd.DataFrame:
    """Return one row per team per match, with goals and points from that team's side."""
    matches = read_columns(path, RESULT_COLUMNS)
    matches["date"] = pd.to_datetime(matches["Date"], dayfirst=True, format="mixed")
    matches["home_goals"] = matches["FTHG"].astype(int)
    matches["away_goals"] = matches["FTAG"].astype(int)

    all_names = set(matches["HomeTeam"]) | set(matches["AwayTeam"])
    unknown = sorted(all_names - set(FOOTBALL_DATA_TO_WIKIPEDIA))
    if unknown:
        raise KeyError(f"Unknown club names in {path.name}: {unknown}. Add them to clubs.py.")

    home = pd.DataFrame(
        {
            "club": matches["HomeTeam"].map(FOOTBALL_DATA_TO_WIKIPEDIA),
            "date": matches["date"],
            "goals_for": matches["home_goals"],
            "goals_against": matches["away_goals"],
        }
    )
    away = pd.DataFrame(
        {
            "club": matches["AwayTeam"].map(FOOTBALL_DATA_TO_WIKIPEDIA),
            "date": matches["date"],
            "goals_for": matches["away_goals"],
            "goals_against": matches["home_goals"],
        }
    )
    team_rows = pd.concat([home, away], ignore_index=True)
    team_rows["points"] = [
        points_for(gf, ga)
        for gf, ga in zip(team_rows["goals_for"], team_rows["goals_against"], strict=True)
    ]
    team_rows["season"] = start_year
    return team_rows


def read_all_results(raw_dir: Path = FOOTBALL_DATA_DIR) -> pd.DataFrame:
    """Read every season file into one table of club-matches."""
    tables = [
        read_season_results(season_file(raw_dir, year), year)
        for year in range(FIRST_PL_SEASON, LAST_PL_SEASON + 1)
    ]
    return pd.concat(tables, ignore_index=True)


def attach_spells(club_matches: pd.DataFrame, spells: pd.DataFrame) -> pd.DataFrame:
    """Give each club-match to the spell that was active at the club on that date.

    When two spells overlap on the same day (a handover), the match goes to the
    spell that started later, because that manager was in charge when the match
    was played. Matches with no spell are left with spell_id missing, so they can
    be counted and checked.
    """
    spells = spells.reset_index(names="spell_id")
    attached = []
    for club, matches in club_matches.groupby("club"):
        club_spells = spells[spells["club"] == club].sort_values("start_date")
        spell_ids = []
        for match_date in matches["date"]:
            active = club_spells[
                (club_spells["start_date"] <= match_date) & (match_date <= club_spells["end_date"])
            ]
            spell_ids.append(active["spell_id"].iloc[-1] if len(active) else None)
        attached.append(matches.assign(spell_id=spell_ids))
    result = pd.concat(attached, ignore_index=True)
    missing = int(result["spell_id"].isna().sum())
    if missing:
        logger.warning(f"{missing} club-matches have no spell in the spells table")
    return result


def summarise_spells(spell_matches: pd.DataFrame, spells: pd.DataFrame) -> pd.DataFrame:
    """Add each spell's matches, points, points per game and goal difference per game."""
    spells = spells.reset_index(names="spell_id")
    played = spell_matches.dropna(subset=["spell_id"]).copy()
    played["spell_id"] = played["spell_id"].astype(int)
    played["goal_difference"] = played["goals_for"] - played["goals_against"]
    totals = played.groupby("spell_id").agg(
        matches=("points", "size"),
        points=("points", "sum"),
        goal_difference=("goal_difference", "sum"),
    )
    summary = spells.merge(totals, left_on="spell_id", right_index=True, how="left")
    summary[["matches", "points", "goal_difference"]] = (
        summary[["matches", "points", "goal_difference"]].fillna(0).astype(int)
    )
    summary["points_per_game"] = (summary["points"] / summary["matches"]).where(
        summary["matches"] > 0
    )
    summary["goal_difference_per_game"] = (summary["goal_difference"] / summary["matches"]).where(
        summary["matches"] > 0
    )
    return summary


def main(
    spells_path: Path = SPELLS_FILE,
    matches_output: Path = SPELL_MATCHES_FILE,
    results_output: Path = SPELL_RESULTS_FILE,
) -> None:
    """Attach every match to a spell, then save the matches and the spell totals."""
    spells = pd.read_parquet(spells_path)
    club_matches = read_all_results()
    spell_matches = attach_spells(club_matches, spells)
    summary = summarise_spells(spell_matches, spells)

    # Check both tables before saving either one, so a bad run writes nothing.
    SPELL_MATCHES_SCHEMA.validate(spell_matches)
    SPELL_RESULTS_SCHEMA.validate(summary)

    for output in (matches_output, results_output):
        output.parent.mkdir(parents=True, exist_ok=True)
    spell_matches.to_parquet(matches_output, index=False)
    summary.to_parquet(results_output, index=False)
    logger.success(f"Saved {len(spell_matches)} club-matches and {len(summary)} spell results")


if __name__ == "__main__":
    main()
