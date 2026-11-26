"""Validation rules for the cleaned spells table.

Every time the cleaning step saves its output, the table is checked against
this schema first. If a refreshed Wikipedia page has missing dates, reversed
dates or impossible tenures, the run stops with a clear error rather than
saving bad data.

pandera is the validation library the project uses (see the python-data-science
skill). Each rule below is written out in plain words so it's easy to change.
"""

import pandera.pandas as pa

SPELLS_SCHEMA = pa.DataFrameSchema(
    columns={
        "name": pa.Column(str, nullable=False),
        "club": pa.Column(str, nullable=False),
        "nationality": pa.Column(str, nullable=True),  # some flags may be missing
        "is_caretaker": pa.Column(bool),
        "is_ongoing": pa.Column(bool),
        "start_date": pa.Column(pa.DateTime, nullable=False),
        "end_date": pa.Column(pa.DateTime, nullable=False),
        "tenure_days": pa.Column(int, pa.Check.ge(0)),
        "pl_tenure_days": pa.Column(int, pa.Check.ge(0)),
        # The day the Wikipedia page was downloaded, so every row says where it came from.
        "snapshot_date": pa.Column(pa.DateTime, nullable=False),
        # Wikipedia's own duration, kept only to compare with tenure_days (open question 8).
        "duration_days": pa.Column(int, pa.Check.ge(0)),
    },
    checks=[
        # A spell cannot end before it starts.
        pa.Check(lambda df: df["end_date"] >= df["start_date"], error="end before start"),
        # Premier League time can never be longer than the whole spell.
        pa.Check(
            lambda df: df["pl_tenure_days"] <= df["tenure_days"], error="PL longer than spell"
        ),
    ],
    strict=True,  # no unexpected extra columns
)


# Club-level matches with the spell each one belongs to (see results.py).
# A match with no spell is allowed: those gaps are known and counted as a warning.
SPELL_MATCHES_SCHEMA = pa.DataFrameSchema(
    columns={
        "club": pa.Column(str, nullable=False),
        "date": pa.Column(pa.DateTime, nullable=False),
        "season": pa.Column(int, pa.Check.between(1992, 2030)),
        "goals_for": pa.Column(int, pa.Check.ge(0)),
        "goals_against": pa.Column(int, pa.Check.ge(0)),
        "points": pa.Column(int, pa.Check.isin([0, 1, 3])),
        "spell_id": pa.Column(float, pa.Check.ge(0), nullable=True),
    },
    checks=[
        # Points must agree with the goals: 3 for a win, 1 for a draw, 0 for a loss.
        pa.Check(
            lambda df: (
                df["points"]
                == df.apply(
                    lambda r: (
                        3
                        if r["goals_for"] > r["goals_against"]
                        else 1
                        if r["goals_for"] == r["goals_against"]
                        else 0
                    ),
                    axis=1,
                )
            ),
            error="points disagree with goals",
        ),
    ],
    strict=True,
)

# One row per spell, with its totals. A spell with no matches has no points per game.
SPELL_RESULTS_SCHEMA = pa.DataFrameSchema(
    columns={
        "name": pa.Column(str, nullable=False),
        "club": pa.Column(str, nullable=False),
        "matches": pa.Column(int, pa.Check.ge(0)),
        "points": pa.Column(int, pa.Check.ge(0)),
        "goal_difference": pa.Column(int),
        "points_per_game": pa.Column(float, pa.Check.in_range(0, 3), nullable=True),
        "goal_difference_per_game": pa.Column(float, pa.Check.in_range(-10, 10), nullable=True),
    },
    checks=[
        pa.Check(lambda df: df["points"] <= 3 * df["matches"], error="more points than 3 a match"),
    ],
    strict=False,  # the spells columns are carried along too
)
