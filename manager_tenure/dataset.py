"""Download and store the raw Wikipedia snapshot (the first step of the pipeline).

Run with `uv run python -m manager_tenure.dataset` (or `make data`).
Add `--refresh` to download a new snapshot even if one already exists.

The raw HTML is saved exactly as downloaded and never edited, next to a
metadata.json recording where it came from, when, and its sha256 hash.
"""

from datetime import UTC, date, datetime
import hashlib
import json
from pathlib import Path

from loguru import logger
import requests
import typer

from manager_tenure.config import (
    METADATA_FILENAME,
    RAW_DATA_DIR,
    REQUEST_TIMEOUT_SECONDS,
    SNAPSHOT_PREFIX,
    USER_AGENT,
    WIKI_URL,
)

app = typer.Typer()


def snapshot_path(raw_dir: Path, snapshot_date: date) -> Path:
    """Return the file path for a snapshot taken on a given date."""
    return raw_dir / f"{SNAPSHOT_PREFIX}_{snapshot_date.isoformat()}.html"


def find_latest_snapshot(raw_dir: Path) -> Path | None:
    """Return the most recent snapshot in raw_dir, or None if there isn't one.

    The ISO date in the filename sorts correctly as text, so the last
    name in sorted order is the newest.
    """
    snapshots = sorted(raw_dir.glob(f"{SNAPSHOT_PREFIX}_*.html"))
    return snapshots[-1] if snapshots else None


def sha256_of_bytes(content: bytes) -> str:
    """Return the sha256 hash of some bytes as a hex string."""
    return hashlib.sha256(content).hexdigest()


def build_metadata(url: str, retrieved_at: datetime, filename: str, content: bytes) -> dict:
    """Describe a snapshot: its source URL, retrieval time (UTC), file and hash."""
    return {
        "url": url,
        "retrieved_at": retrieved_at.isoformat(timespec="seconds"),
        "filename": filename,
        "sha256": sha256_of_bytes(content),
        "bytes": len(content),
    }


def download_page(url: str) -> bytes:
    """Download a web page politely and return its raw bytes."""
    logger.info(f"Downloading {url}")
    response = requests.get(
        url, headers={"User-Agent": USER_AGENT}, timeout=REQUEST_TIMEOUT_SECONDS
    )
    response.raise_for_status()
    logger.info(f"Downloaded {len(response.content):,} bytes")
    return response.content


def save_snapshot(content: bytes, raw_dir: Path, url: str, retrieved_at: datetime) -> Path:
    """Write the raw HTML and its metadata.json into raw_dir; return the HTML path."""
    raw_dir.mkdir(parents=True, exist_ok=True)
    html_path = snapshot_path(raw_dir, retrieved_at.date())
    with html_path.open("xb") as snapshot_file:
        snapshot_file.write(content)

    metadata = build_metadata(url, retrieved_at, html_path.name, content)
    metadata_path = raw_dir / METADATA_FILENAME
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")

    logger.info(f"Saved snapshot to {html_path} (sha256 {metadata['sha256'][:12]}...)")
    return html_path


@app.command()
def main(
    refresh: bool = typer.Option(False, help="Download a new snapshot even if one exists."),
    raw_dir: Path = RAW_DATA_DIR,
) -> None:
    """Make sure a raw snapshot exists, downloading one only if needed."""
    existing = find_latest_snapshot(raw_dir)
    if existing and not refresh:
        logger.info(f"Using existing snapshot {existing.name} (pass --refresh to re-download)")
        return

    content = download_page(WIKI_URL)
    save_snapshot(content, raw_dir, WIKI_URL, datetime.now(UTC))
    logger.success("Raw snapshot ready.")


if __name__ == "__main__":
    app()
