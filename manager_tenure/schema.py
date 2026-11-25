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
        "pl_start_date": pa.Column(pa.DateTime, nullable=False),
        "pl_tenure_days": pa.Column(int, pa.Check.ge(0)),
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
