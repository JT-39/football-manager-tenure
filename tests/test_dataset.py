"""Tests for the raw snapshot helpers in manager_tenure/dataset.py.

None of these touch the network: they use pytest's tmp_path (a fresh
temporary folder per test) and replace download_page with a fake.
"""

from datetime import UTC, date, datetime
import hashlib
import json

from manager_tenure import dataset

URL = "https://example.org/page"
WHEN = datetime(2026, 11, 22, 21, 30, 5, tzinfo=UTC)


def test_snapshot_path_uses_iso_date(tmp_path):
    path = dataset.snapshot_path(tmp_path, date(2026, 1, 5))
    assert path == tmp_path / "wiki_premier_league_managers_2026-01-05.html"


def test_find_latest_snapshot_returns_none_when_empty(tmp_path):
    assert dataset.find_latest_snapshot(tmp_path) is None


def test_find_latest_snapshot_picks_newest_date(tmp_path):
    for day in ["2025-12-31", "2026-11-22", "2026-02-01"]:
        (tmp_path / f"wiki_premier_league_managers_{day}.html").write_text("x")
    (tmp_path / "metadata.json").write_text("{}")  # should be ignored

    latest = dataset.find_latest_snapshot(tmp_path)
    assert latest.name == "wiki_premier_league_managers_2026-11-22.html"


def test_sha256_matches_known_value():
    # Known sha256 of the bytes b"abc" (a standard test vector).
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert dataset.sha256_of_bytes(b"abc") == expected


def test_build_metadata_has_expected_fields():
    meta = dataset.build_metadata(URL, WHEN, "snap.html", b"<html></html>")
    assert meta == {
        "url": URL,
        "retrieved_at": "2026-11-22T21:30:05+00:00",
        "filename": "snap.html",
        "sha256": hashlib.sha256(b"<html></html>").hexdigest(),
        "bytes": 13,
    }


def test_save_snapshot_writes_html_and_metadata(tmp_path):
    content = b"<html>managers</html>"
    html_path = dataset.save_snapshot(content, tmp_path / "raw", URL, WHEN)

    assert html_path.read_bytes() == content
    meta = json.loads((tmp_path / "raw" / "metadata.json").read_text())
    assert meta["filename"] == html_path.name
    assert meta["sha256"] == dataset.sha256_of_bytes(content)


def test_main_skips_download_when_snapshot_exists(tmp_path, monkeypatch):
    (tmp_path / "wiki_premier_league_managers_2026-01-01.html").write_text("old")
    calls = []
    monkeypatch.setattr(dataset, "download_page", lambda url: calls.append(url) or b"new")

    dataset.main(refresh=False, raw_dir=tmp_path)
    assert calls == []


def test_main_downloads_when_refresh_is_passed(tmp_path, monkeypatch):
    (tmp_path / "wiki_premier_league_managers_2026-01-01.html").write_text("old")
    monkeypatch.setattr(dataset, "download_page", lambda url: b"new")

    dataset.main(refresh=True, raw_dir=tmp_path)
    assert (tmp_path / "metadata.json").exists()
