"""Tests for the JSON export used by the website (manager_tenure/export.py)."""

import json

import pandas as pd

from manager_tenure import export
from manager_tenure.config import SPELLS_JSON_FILE


def small_table() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "name": ["Stewart Houston", "Mikel Arteta"],
            "nationality": [None, "Spain"],
            "is_caretaker": [True, False],
            "start_date": pd.to_datetime(["1995-02-22", "2019-12-22"]),
            "end_date": pd.to_datetime(["1995-06-08", "2026-11-23"]),
            "tenure_days": [106, 2528],
            "snapshot_date": pd.to_datetime(["2026-11-23", "2026-11-23"]),
        }
    )


def test_dates_become_plain_text():
    records = export.to_web_records(small_table())
    assert records[0]["start_date"] == "1995-02-22"
    assert records[1]["end_date"] == "2026-11-23"


def test_missing_values_become_none_so_json_writes_null():
    records = export.to_web_records(small_table())
    assert records[0]["nationality"] is None
    assert records[1]["nationality"] == "Spain"


def test_numbers_and_booleans_keep_their_types():
    record = export.to_web_records(small_table())[0]
    assert record["tenure_days"] == 106 and isinstance(record["tenure_days"], int)
    assert record["is_caretaker"] is True


def test_write_creates_a_json_array(tmp_path):
    output = tmp_path / "nested" / "spells.json"
    export.write_spells_json(small_table(), output)
    loaded = json.loads(output.read_text())
    assert len(loaded) == 2
    assert loaded[1]["name"] == "Mikel Arteta"


def test_the_real_export_has_one_entry_per_spell():
    if not SPELLS_JSON_FILE.exists():
        return  # make data has not been run yet
    loaded = json.loads(SPELLS_JSON_FILE.read_text())
    assert len(loaded) == 521
