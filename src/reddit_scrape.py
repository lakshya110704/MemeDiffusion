# src/reddit_scrape.py
"""
Reddit scraper using PRAW that reads credentials from .env and queries from src.config.
Saves raw JSONL to data/raw/<name>.jsonl and a processed CSV to data/processed/<name>_clean.csv.
"""

import sys
from pathlib import Path
import os
import json
import csv
import time
from dotenv import load_dotenv
import praw

# Add project root to sys.path to allow importing src.config
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load .env explicitly from the project root
load_dotenv(dotenv_path=ROOT / '.env')

# Import project configuration
from src.config import RAW_DIR, PROC_DIR, SCRAPE_ITEMS, MAX_RESULTS

# Read credentials from environment
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
USER_AGENT = os.getenv("REDDIT_USER_AGENT")

print("DEBUG: Using .env from:", ROOT / '.env')
print("DEBUG: REDDIT_CLIENT_ID present:", bool(CLIENT_ID))
print("DEBUG: REDDIT_USERNAME:", USERNAME)

if not all([CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD, USER_AGENT]):
    raise SystemExit("Missing one or more Reddit credentials in .env. Please check .env in project root.")

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    username=USERNAME,
    password=PASSWORD,
    user_agent=USER_AGENT,
)


def save_jsonl(items, out_path: Path):
    """Save raw data to a JSONL file."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        for it in items:
            fh.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"Wrote raw jsonl -> {out_path}")


def save_csv(rows, out_csv: Path):
    """Save cleaned data to CSV for later processing."""
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "date", "content", "user_username", "replyCount", "likeCount", "subreddit", "content_type"]
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote processed csv -> {out_csv}")


def scrape_query(query, limit):
    """Perform a Reddit search for the given query and return items + rows."""
    print(f"\nSearching for: {query!r}  (limit={limit})")
    items = []
    rows = []
    try:
        for i, submission in enumerate(reddit.subreddit("all").search(query, limit=limit)):
            raw = {
                "id": submission.id,
                "created_utc": int(submission.created_utc),
                "title": submission.title,
                "selftext": submission.selftext or "",
                "url": submission.url,
                "subreddit": str(submission.subreddit),
                "author": str(submission.author) if submission.author else None,
                "score": submission.score,
                "num_comments": submission.num_comments,
            }
            items.append(raw)

            rows.append({
                "id": raw["id"],
                "date": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(raw["created_utc"])),
                "content": (raw["title"] + " " + raw["selftext"]).strip(),
                "user_username": raw["author"] or "deleted",
                "replyCount": raw["num_comments"],
                "likeCount": raw["score"],
                "subreddit": raw["subreddit"],
                "content_type": ""  # will be filled by caller before saving
            })

            if (i + 1) % 50 == 0:
                print(f"  collected {(i + 1)}")
    except Exception as e:
        print("Error during PRAW search:", type(e).__name__, e)
    if not items:
        print("Warning: no items were found for this query (empty results). Try a different query or check rate limits.")
    return items, rows


def main():
    """Main function to iterate over queries and save results."""
    for item in SCRAPE_ITEMS:
        name = item.get("name")
        query = item.get("query")
        ctype = item.get("type", "")

        out_raw = RAW_DIR / f"{name}.jsonl"
        out_csv = PROC_DIR / f"{name}_clean.csv"

        items, rows = scrape_query(query, MAX_RESULTS)

        # attach content_type
        for r in rows:
            r["content_type"] = ctype

        save_jsonl(items, out_raw)
        save_csv(rows, out_csv)


if __name__ == "__main__":
    main()