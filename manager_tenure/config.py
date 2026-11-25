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

# The cleaned table of spells. It is final output, so it lives in data/processed/
# and is rebuilt by `make data` rather than committed to git.
SPELLS_FILE = PROCESSED_DATA_DIR / "spells.parquet"
# The same table as JSON, for the website. Built from SPELLS_FILE by export.py.
SPELLS_JSON_FILE = PROCESSED_DATA_DIR / "spells.json"

# Premier League membership, by season (see premier_league.py).
# football-data.co.uk publishes one CSV per season, listing every match. The
# files are named by season, e.g. E0_2526.csv for 2025–26.
FOOTBALL_DATA_BASE_URL = "https://www.football-data.co.uk/mmz4281"
FOOTBALL_DATA_DIR = RAW_DATA_DIR / "football_data"
# The first file is the 1993–94 season; there is no file for 1992–93 (see clubs.py).
FIRST_PL_SEASON = 1993
LAST_PL_SEASON = 2026  # 2026 is the 2026–27 season, still in progress at the snapshot date
# Each club's Premier League membership, one row per club per season.
PREMIER_LEAGUE_SEASONS_FILE = PROCESSED_DATA_DIR / "premier_league_seasons.parquet"
