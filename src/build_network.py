# src/build_network.py
"""
Builds a diffusion-style network graph from the processed Reddit CSVs.
Each subreddit and author is a node; edges connect authors to the subreddits they post in.
"""

import sys
from pathlib import Path

# --- Fix: ensure project root is in the Python path ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# ------------------------------------------------------

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from src.config import PROC_DIR


def load_data():
    """Load all processed CSVs from data/processed."""
    csvs = list(PROC_DIR.glob("*_clean.csv"))
    if not csvs:
        raise SystemExit("No processed CSV files found. Run reddit_scrape.py first.")
    dfs = []
    for f in csvs:
        df = pd.read_csv(f)
        df["source_file"] = f.name
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def build_network(df):
    """Build a bipartite graph: authors ↔ subreddits."""
    G = nx.Graph()
    for _, row in df.iterrows():
        author = row["user_username"]
        subreddit = row["subreddit"]
        if pd.notna(author) and pd.notna(subreddit):
            G.add_node(author, type="author")
            G.add_node(subreddit, type="subreddit")
            G.add_edge(author, subreddit, weight=row["likeCount"])
    return G


def visualize_network(G):
    """Quick visualization of the diffusion graph."""
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=0.5)
    nx.draw(
        G,
        pos,
        node_color="skyblue",
        node_size=40,
        edge_color="gray",
        linewidths=0.2,
        alpha=0.7,
        with_labels=False,
    )
    plt.title("Meme / Hashtag / Misinformation Diffusion Network", fontsize=14)
    plt.tight_layout()
    plt.show()


def main():
    df = load_data()
    print(f"Loaded {len(df)} posts from {df['source_file'].nunique()} files.")
    G = build_network(df)
    print(f"Graph: {len(G.nodes())} nodes, {len(G.edges())} edges.")
    visualize_network(G)


if __name__ == "__main__":
    main()