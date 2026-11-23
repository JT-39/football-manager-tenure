from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Source data: Wikipedia's "List of Premier League managers" (CC BY-SA).
WIKI_URL = "https://en.wikipedia.org/wiki/List_of_Premier_League_managers"

# Wikipedia asks automated clients to identify themselves with a descriptive
# User-Agent: https://meta.wikimedia.org/wiki/User-Agent_policy
USER_AGENT = "manager-tenure-pipeline/0.1 (open-source educational data project; python-requests)"
REQUEST_TIMEOUT_SECONDS = 30

# Raw snapshot files are named <prefix>_<YYYY-MM-DD>.html
SNAPSHOT_PREFIX = "wiki_premier_league_managers"
# Each snapshot gets its own metadata file next to it, e.g.
# wiki_premier_league_managers_2026-11-23.metadata.json
METADATA_SUFFIX = ".metadata.json"

# Cleaning settings (used by features.py)
# The first Premier League matches were played on 15 August 1992. Spells that
# started earlier (e.g. Ferguson, appointed 1986) only count as Premier League
# time from this date.
PREMIER_LEAGUE_START = "1992-08-15"
# The cleaned table of spells, read by later steps and (eventually) the website.
SPELLS_FILE = INTERIM_DATA_DIR / "spells.parquet"
