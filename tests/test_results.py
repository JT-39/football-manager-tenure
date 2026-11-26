"""Tests for the spell results (manager_tenure/results.py).

The small tests use hand-made tables. The last tests check the real outputs
produced by `make data`.
"""

import pandas as pd
import pytest

from manager_tenure import results
from manager_tenure.config import SPELL_MATCHES_FILE, SPELL_RESULTS_FILE


@pytest.mark.parametrize(
    ("goals_for", "goals_against", "expected"),
    [(2, 0, 3), (1, 1, 1), (0, 2, 0), (0, 0, 1)],
)
def test_points_for_a_result(goals_for, goals_against, expected):
    assert results.points_for(goals_for, goals_against) == expected


def test_each_match_gives_points_to_both_sides(tmp_path):
    path = tmp_path / "E0_9394.csv"
    path.write_text(
        "Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR\n"
        "E0,14/08/93,,Arsenal,Chelsea,2,0,H\n"
        "E0,21/08/93,,Chelsea,Arsenal,1,1,D\n"
    )
    rows = results.read_season_results(path, 1993)
    arsenal = rows[rows["club"] == "Arsenal"].sort_values("date")
    assert arsenal["points"].tolist() == [3, 1]
    assert arsenal["goals_for"].tolist() == [2, 1]
    assert arsenal["goals_against"].tolist() == [0, 1]
    assert rows.loc[rows["club"] == "Chelsea", "points"].sum() == 1


def test_unknown_club_in_results_stops_with_a_clear_error(tmp_path):
    path = tmp_path / "E0_9394.csv"
    path.write_text(
        "Div,Date,Time,HomeTeam,AwayTeam,FTHG,FTAG,FTR\nE0,14/08/93,,Atlantis,Chelsea,1,0,H\n"
    )
    with pytest.raises(KeyError, match="Atlantis"):
        results.read_season_results(path, 1993)


def _matches(club: str, dates: list[str]) -> pd.DataFrame:
    return pd.DataFrame({"club": club, "date": pd.to_datetime(dates)})


def _spells() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["Old Boss", "New Boss"],
            "club": ["Arsenal", "Arsenal"],
            "start_date": pd.to_datetime(["2000-01-01", "2002-01-01"]),
            "end_date": pd.to_datetime(["2002-01-01", "2004-01-01"]),
        }
    )


def test_a_match_goes_to_the_spell_active_on_that_day():
    attached = results.attach_spells(_matches("Arsenal", ["2000-06-01", "2003-06-01"]), _spells())
    assert attached["spell_id"].tolist() == [0, 1]


def test_on_a_handover_day_the_later_spell_gets_the_match():
    # Both spells include 1 January 2002. The manager who started that day was in charge.
    attached = results.attach_spells(_matches("Arsenal", ["2002-01-01"]), _spells())
    assert attached["spell_id"].tolist() == [1]


def test_a_match_outside_every_spell_is_left_unattributed():
    attached = results.attach_spells(_matches("Arsenal", ["1999-06-01"]), _spells())
    assert pd.isna(attached["spell_id"].iloc[0])


def test_points_per_game_and_goal_difference_per_game():
    spells = _spells()
    matches = pd.DataFrame(
        {
            "club": ["Arsenal", "Arsenal"],
            "spell_id": [0.0, 0.0],
            "points": [3, 0],
            "goals_for": [2, 0],
            "goals_against": [0, 3],
        }
    )
    summary = results.summarise_spells(matches, spells)
    old = summary[summary["name"] == "Old Boss"].iloc[0]
    assert old["matches"] == 2
    assert old["points"] == 3
    assert old["points_per_game"] == pytest.approx(1.5)
    assert old["goal_difference_per_game"] == pytest.approx(-0.5)


def test_a_spell_with_no_matches_has_no_points_per_game():
    summary = results.summarise_spells(
        pd.DataFrame(columns=["club", "spell_id", "points", "goals_for", "goals_against"]),
        _spells(),
    )
    assert summary["matches"].tolist() == [0, 0]
    assert summary["points_per_game"].isna().all()


# ---- The real outputs ---------------------------------------------------------


def test_real_spell_results_cover_every_spell():
    summary = pd.read_parquet(SPELL_RESULTS_FILE)
    assert len(summary) == 521


def test_fergusons_league_matches_are_counted():
    # 1993–94 to 2012–13: 2 seasons of 42 matches, then 18 of 38.
    summary = pd.read_parquet(SPELL_RESULTS_FILE)
    fergie = summary[summary["name"] == "Alex Ferguson"].iloc[0]
    assert fergie["matches"] == 2 * 42 + 18 * 38


def test_only_a_few_club_matches_lack_a_spell():
    matches = pd.read_parquet(SPELL_MATCHES_FILE)
    assert matches["spell_id"].isna().sum() < 20  # known gaps in the Wikipedia dates


def test_schema_rejects_points_that_disagree_with_goals():
    from pandera.errors import SchemaError, SchemaErrors

    from manager_tenure.schema import SPELL_MATCHES_SCHEMA

    bad = pd.DataFrame(
        {
            "club": ["Arsenal"],
            "date": pd.to_datetime(["2000-08-19"]),
            "season": [2000],
            "goals_for": [2],
            "goals_against": [0],
            "points": [0],  # a 2-0 win must give 3 points
            "spell_id": [0.0],
        }
    )
    with pytest.raises((SchemaError, SchemaErrors)):
        SPELL_MATCHES_SCHEMA.validate(bad)


def test_main_writes_both_outputs_into_new_folders(tmp_path):
    # Runs the real step, with both outputs going to folders that don't exist yet.
    matches_out = tmp_path / "a" / "matches.parquet"
    results_out = tmp_path / "b" / "results.parquet"
    results.main(matches_output=matches_out, results_output=results_out)
    assert matches_out.exists() and results_out.exists()
