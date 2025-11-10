# src/scrape.py
import subprocess
import shlex
from pathlib import Path
from config import RAW_DIR, SCRAPE_ITEMS, MAX_RESULTS

def run_snscrape(query, out_path, max_results=500):
    """
    Uses snscrape CLI to fetch tweets based on query.
    Saves the results as a JSONL file in data/raw.
    """
    cmd = f"snscrape --jsonl --max-results {max_results} \"twitter-search '{query}'\""
    print(f"Running:\n{cmd}\n")
    
    with open(out_path, "w", encoding="utf-8") as f:
        proc = subprocess.Popen(shlex.split(cmd), stdout=f, stderr=subprocess.PIPE, text=True)
        _, err = proc.communicate()
        if proc.returncode != 0:
            print("❌ snscrape error:", err)
        else:
            print(f"✅ Saved: {out_path}")

def main():
    for item in SCRAPE_ITEMS:
        out_file = RAW_DIR / f"{item['name']}.jsonl"
        print(f"\nScraping: {item['name']} → {out_file}")
        run_snscrape(item['query'], out_file, MAX_RESULTS)

if __name__ == "__main__":
    main()