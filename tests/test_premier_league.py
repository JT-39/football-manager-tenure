"""Tests for the Premier League membership table (manager_tenure/premier_league.py).

Most tests use tiny CSV files written to a temporary folder. The last few read the
real season files saved in data/raw/football_data/, which are committed to git.
"""

import pandas as pd
import pytest

from manager_tenure import premier_league
from manager_tenure.clubs import FOOTBALL_DATA_TO_WIKIPEDIA, FOUNDING_CLUBS_1992
from manager_tenure.config import FOOTBALL_DATA_DIR


def test_season_code_matches_football_data_names():
    assert premier_league.season_code(1993) == "9394"
    assert premier_league.season_code(2025) == "2526"
    assert premier_league.season_code(1999) == "9900"


def test_read_matches_keeps_short_and_long_rows(tmp_path):
    # Older files have rows with a different number of columns from the header.
    # Both shapes must be read, and a blank row must be skipped.
    path = tmp_path / "E0_9394.csv"
    path.write_text(
        "Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG\n"
        "E0,14/08/93,,Arsenal,Chelsea,1,0\n"  # the same number of columns as the header
        "E0,21/08/93,,Chelsea,Arsenal,0,0,extra,extra,extra\n"  # longer than the header
        "E0,28/08/93\n"  # too short to hold the teams: skipped
        ",,,,,,\n"  # blank: skipped
    )
    matches = premier_league.read_matches(path)
    assert len(matches) == 2
    assert matches["home"].tolist() == ["Arsenal", "Chelsea"]
    assert matches["date"].iloc[0] == pd.Timestamp("1993-08-14")


def test_season_memberships_gives_first_and_last_match_per_club(tmp_path):
    path = tmp_path / "E0_9394.csv"
    path.write_text(
        "Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG\n"
        "E0,14/08/93,,Arsenal,Chelsea,1,0\n"
        "E0,08/05/94,,Chelsea,Arsenal,0,0\n"
    )
    seasons = premier_league.season_memberships(path, 1993)
    arsenal = seasons[seasons["club"] == "Arsenal"].iloc[0]
    assert arsenal["start_date"] == pd.Timestamp("1993-08-14")
    # The end is the day after the last match, so the last match day counts.
    assert arsenal["end_date"] == pd.Timestamp("1994-05-09")
    assert arsenal["season"] == 1993


def test_unknown_club_name_stops_with_a_clear_error(tmp_path):
    path = tmp_path / "E0_9394.csv"
    path.write_text(
        "Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG\nE0,14/08/93,,Atlantis,Chelsea,1,0\n"
    )
    with pytest.raises(KeyError, match="Atlantis"):
        premier_league.season_memberships(path, 1993)


def test_founding_clubs_are_22_known_names():
    assert len(FOUNDING_CLUBS_1992) == 22
    assert set(FOUNDING_CLUBS_1992) <= set(FOOTBALL_DATA_TO_WIKIPEDIA.values())


def test_season_file_names_are_unique():
    names = {premier_league.season_file(FOOTBALL_DATA_DIR, y).name for y in range(1993, 2027)}
    assert len(names) == 34


# ---- The real season files --------------------------------------------------


def test_every_real_season_has_the_full_number_of_matches():
    # 22 clubs play 462 matches a season, and 20 clubs play 380. Counting every
    # season catches the bug where rows were silently dropped.
    for year in range(1993, 2026):  # completed seasons
        matches = premier_league.read_matches(premier_league.season_file(FOOTBALL_DATA_DIR, year))
        expected = 462 if year in (1993, 1994) else 380
        assert len(matches) == expected, f"season {year}"
    # 2026–27 is still being played, so it has some matches but not a full season.
    current = premier_league.read_matches(premier_league.season_file(FOOTBALL_DATA_DIR, 2026))
    assert 0 < len(current) < 380


def test_real_membership_table_shape():
    memberships = premier_league.build_memberships()
    assert len(memberships[memberships["season"] == 1992]) == 22
    assert len(memberships[memberships["season"] == 1994]) == 22
    assert len(memberships[memberships["season"] == 2000]) == 20
    assert (memberships["end_date"] > memberships["start_date"]).all()


def test_southampton_membership_matches_their_history():
    memberships = premier_league.build_memberships()
    southampton = memberships[memberships["club"] == "Southampton"]
    seasons = set(southampton["season"])
    assert 1992 in seasons and 2004 in seasons  # top flight 1992 to 2005
    assert 2008 not in seasons  # relegated, so not in the Premier League
    assert 2024 in seasons  # back in the Premier League for 2024–25


# ---- Summer breaks ------------------------------------------------------------


def _club_seasons(club: str, seasons: list[int]) -> pd.DataFrame:
    """A small membership table: one row per season, with the season's first and last match."""
    return pd.DataFrame(
        {
            "club": club,
            "season": seasons,
            "start_date": [pd.Timestamp(f"{y}-08-15") for y in seasons],
            "end_date": [pd.Timestamp(f"{y + 1}-05-15") for y in seasons],
        }
    )


def test_summer_between_two_top_flight_seasons_counts():
    periods = premier_league.league_periods(_club_seasons("Arsenal", [2000, 2001]))
    assert len(periods) == 1
    # One unbroken period, so the summer of 2001 is inside it.
    assert periods.iloc[0]["start_date"] == pd.Timestamp("2000-08-15")
    assert periods.iloc[0]["end_date"] == pd.Timestamp("2002-05-15")


def test_promotion_and_relegation_summers_do_not_count():
    # In the league 2000 and 2001, out in 2002, back in 2003: two separate periods.
    periods = premier_league.league_periods(_club_seasons("Arsenal", [2000, 2001, 2003]))
    assert len(periods) == 2
    assert periods.iloc[0]["end_date"] == pd.Timestamp("2002-05-15")
    assert periods.iloc[1]["start_date"] == pd.Timestamp("2003-08-15")


def test_each_club_gets_its_own_periods():
    both = pd.concat(
        [_club_seasons("Arsenal", [2000, 2001]), _club_seasons("Chelsea", [2005])],
        ignore_index=True,
    )
    periods = premier_league.league_periods(both)
    assert sorted(periods["club"]) == ["Arsenal", "Chelsea"]
