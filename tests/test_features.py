"""Tests for the cleaning steps in manager_tenure/features.py (milestone 1b exercises).

These fail until each function is written. Work through them in order:

    uv run pytest tests/test_features.py -k exercise1     # just one exercise
    make test                                             # everything

Most tests use tiny hand-made DataFrames, so it's clear what goes in and what
should come out. The last section runs the whole pipeline on the real
snapshot and checks a few well-known facts.
"""

from datetime import date

import pandas as pd
from pandera.errors import SchemaError, SchemaErrors
import pytest

from manager_tenure import features, premier_league
from manager_tenure.config import RAW_DATA_DIR
from manager_tenure.schema import SPELLS_SCHEMA

# Pinned to the dated snapshot the known-fact checks were written against.
# Production code always uses the newest snapshot; tests must not, or a routine
# refresh would break them even when the cleaning code is still correct.
SNAPSHOT = RAW_DATA_DIR / "wiki_premier_league_managers_2026-11-23.html"
AS_OF = date(2026, 11, 23)


# ---- Exercise 1: read_spells_table -------------------------------------------


def test_exercise1_reads_the_spells_table():
    spells = features.read_spells_table(SNAPSHOT)
    assert len(spells) == 521
    assert "Duration (days)" in spells.columns
    assert spells.loc[0, "Name"] == "George Graham"


# ---- Exercise 2: tidy_columns ------------------------------------------------


def test_exercise2_renames_and_drops_columns():
    raw = pd.DataFrame(
        {
            "Name": ["George Graham"],
            "Nat.": [None],
            "Club": ["Arsenal"],
            "From": ["14 May 1986"],
            "Until": ["21 February 1995"],
            "Duration (days)": [3205],
            "Years in League": ["1992–1995"],  # dropped: match data is used instead
            "Ref.": ["[8]"],
            "nationality": ["Scotland"],
        }
    )
    tidy = features.tidy_columns(raw)
    assert list(tidy.columns) == [
        "name",
        "club",
        "from",
        "until",
        "duration_days",
        "nationality",
    ]


# ---- Exercise 3: flag_caretakers ---------------------------------------------


def test_exercise3_flags_caretakers_and_cleans_names():
    spells = pd.DataFrame({"name": ["Stewart Houston ‡", "Mikel Arteta †", "George Graham"]})
    result = features.flag_caretakers(spells)
    assert result["name"].tolist() == ["Stewart Houston", "Mikel Arteta", "George Graham"]
    assert result["is_caretaker"].tolist() == [True, False, False]


def test_exercise3_does_not_change_the_input():
    # Good habit: return a new DataFrame rather than editing the one passed in.
    spells = pd.DataFrame({"name": ["Stewart Houston ‡"]})
    features.flag_caretakers(spells)
    assert spells["name"].tolist() == ["Stewart Houston ‡"]


# ---- Exercise 4: parse_dates -------------------------------------------------


def test_exercise4_parses_dates_and_handles_present():
    spells = pd.DataFrame(
        {
            "from": ["14 May 1986", "22 December 2019"],
            "until": ["21 February 1995", "Present*"],
        }
    )
    result = features.parse_dates(spells, as_of=AS_OF)
    assert result["start_date"].tolist() == [
        pd.Timestamp("1986-05-14"),
        pd.Timestamp("2019-12-22"),
    ]
    assert result["end_date"].tolist() == [pd.Timestamp("1995-02-21"), pd.Timestamp("2026-11-23")]
    assert result["is_ongoing"].tolist() == [False, True]
    assert "from" not in result.columns and "until" not in result.columns


def test_exercise4_ignores_wikipedia_footnote_markers():
    # Real data quirk: some dates have footnote letters stuck on the end.
    spells = pd.DataFrame({"from": ["30 August 2022[a]"], "until": ["Present*"]})
    result = features.parse_dates(spells, as_of=AS_OF)
    assert result.loc[0, "start_date"] == pd.Timestamp("2022-08-30")


# ---- Exercise 5: add_tenure --------------------------------------------------


def test_premier_league_days_only_counts_days_inside_seasons():
    # Eddie Howe at Bournemouth: 2012 to 2020, but the club was in the Premier League
    # only from the 2015 season (from 8 August 2015) until the last match in 2020.
    seasons = [(pd.Timestamp("2015-08-08"), pd.Timestamp("2020-05-18"))]
    days = features.premier_league_days(
        pd.Timestamp("2012-10-12"), pd.Timestamp("2020-08-01"), seasons
    )
    assert days == (pd.Timestamp("2020-05-18") - pd.Timestamp("2015-08-08")).days


def test_exercise5_splits_total_and_premier_league_tenure():
    spells = pd.DataFrame(
        {
            "club": ["Arsenal", "Arsenal"],
            "start_date": pd.to_datetime(["1986-05-14", "1996-10-01"]),
            "end_date": pd.to_datetime(["1995-02-21", "2018-05-13"]),
        }
    )
    memberships = pd.DataFrame(
        {
            "club": ["Arsenal", "Arsenal"],
            "start_date": pd.to_datetime(["1992-08-15", "1996-08-17"]),
            "end_date": pd.to_datetime(["1993-05-11", "2018-05-20"]),
        }
    )
    result = features.add_tenure(spells, memberships=memberships)
    # Total time in charge, including before the Premier League existed.
    assert result["tenure_days"].tolist() == [3205, 7894]
    # Only the days inside the Premier League seasons count.
    assert result["pl_tenure_days"].tolist() == [
        (pd.Timestamp("1993-05-11") - pd.Timestamp("1992-08-15")).days,
        (pd.Timestamp("2018-05-13") - pd.Timestamp("1996-10-01")).days,
    ]


# ---- Exercise 6 (stretch): read_nationalities --------------------------------


def test_exercise6_reads_nationality_from_flags():
    nationalities = features.read_nationalities(SNAPSHOT)
    assert len(nationalities) == 521  # one per spell, in table order
    assert nationalities[0] == "Scotland"  # George Graham
    assert nationalities.count("England") > 200


# ---- Whole pipeline on the real snapshot: well-known facts -------------------


@pytest.fixture(scope="module")
def spells():
    """The fully cleaned table, built once and shared by the tests below."""
    table = features.read_spells_table(SNAPSHOT)
    table["nationality"] = features.read_nationalities(SNAPSHOT)
    return (
        table.pipe(features.tidy_columns)
        .pipe(features.flag_caretakers)
        .pipe(features.parse_dates, as_of=AS_OF)
        .pipe(features.add_tenure, memberships=premier_league.build_memberships())
    )


def test_ferguson_spell(spells):
    fergie = spells[spells["name"] == "Alex Ferguson"].iloc[0]
    assert fergie["club"] == "Manchester United"
    assert fergie["nationality"] == "Scotland"
    assert fergie["start_date"].year == 1986
    assert fergie["end_date"].year == 2013
    # Total time in charge, and only the days Manchester United were in the Premier League.
    assert fergie["tenure_days"] == 9704
    assert 0 < fergie["pl_tenure_days"] < fergie["tenure_days"]


def test_no_markers_left_in_names(spells):
    assert not spells["name"].str.contains("[†‡§]").any()


def test_ongoing_spells_end_on_snapshot_day(spells):
    ongoing = spells[spells["is_ongoing"]]
    assert len(ongoing) == 20  # one per current Premier League club
    assert (ongoing["end_date"] == pd.Timestamp(AS_OF)).all()


def test_no_negative_tenures(spells):
    assert (spells["tenure_days"] >= 0).all()
    assert (spells["pl_tenure_days"] <= spells["tenure_days"]).all()


# ---- Guards added after the PR review ------------------------------------------


def test_read_spells_table_refuses_two_matching_tables(tmp_path, monkeypatch):
    fake_tables = [pd.DataFrame({"Duration (days)": [1]}), pd.DataFrame({"Duration": [2]})]
    monkeypatch.setattr(features.pd, "read_html", lambda *args, **kwargs: fake_tables)
    with pytest.raises(ValueError, match="Expected one spells table"):
        features.read_spells_table(tmp_path / "anything.html")


def test_tidy_columns_reports_a_missing_column():
    raw = pd.DataFrame({"Name": ["x"], "Club": ["y"]})  # the others are missing
    with pytest.raises(KeyError, match="missing expected columns"):
        features.tidy_columns(raw)


def test_schema_rejects_a_spell_that_ends_before_it_starts():
    spells = pd.DataFrame(
        {
            "name": ["Someone"],
            "club": ["Somewhere"],
            "nationality": ["England"],
            "is_caretaker": [False],
            "is_ongoing": [False],
            "start_date": pd.to_datetime(["2000-01-02"]),
            "end_date": pd.to_datetime(["2000-01-01"]),
            "tenure_days": [-1],
            "duration_days": [-1],
            "pl_tenure_days": [-1],
            "snapshot_date": pd.to_datetime(["2026-11-23"]),
        }
    )
    with pytest.raises((SchemaError, SchemaErrors)):
        SPELLS_SCHEMA.validate(spells)
