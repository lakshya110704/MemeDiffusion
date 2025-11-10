# src/config.py
from pathlib import Path

# Base project directory
BASE_DIR = Path(__file__).resolve().parents[1]

# Data directories
RAW_DIR = BASE_DIR / "data" / "raw"
PROC_DIR = BASE_DIR / "data" / "processed"

# Ensure the folders exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROC_DIR.mkdir(parents=True, exist_ok=True)

# Items to scrape (query names + search keywords)
SCRAPE_ITEMS = [
    {"name": "meme_1", "query": "distracted boyfriend", "type": "meme"},
    {"name": "hashtag_1", "query": "#Oscars2025", "type": "hashtag"},
    {"name": "misinfo_1", "query": "fake cure for covid", "type": "misinformation"},
]

# Max posts per query
MAX_RESULTS = 200