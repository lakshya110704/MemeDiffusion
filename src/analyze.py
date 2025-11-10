# src/analyze.py
"""
Compute network metrics and top influencers per content_type.
- Loads processed CSVs from data/processed (expects *_clean.csv)
- Builds an author<->subreddit bipartite graph and also a projected author-author graph
- Computes per-category metrics and saves:
    - data/processed/graph_metrics_summary.csv
    - data/processed/top_influencers.csv
- Prints a quick summary to the terminal.
"""

import sys
from pathlib import Path
import pandas as pd
import networkx as nx
import numpy as np

# ensure project root is importable when running the script directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PROC_DIR

OUT_SUMMARY = Path(PROC_DIR) / "graph_metrics_summary.csv"
OUT_INFLUENCERS = Path(PROC_DIR) / "top_influencers.csv"


def load_processed():
    csvs = list(Path(PROC_DIR).glob("*_clean.csv"))
    if not csvs:
        raise SystemExit("No processed CSV files found in data/processed. Run scraper first.")
    dfs = []
    for p in csvs:
        df = pd.read_csv(p)
        df["source_file"] = p.name
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    # normalize common column names
    if "user_username" not in df.columns and "user.username" in df.columns:
        df = df.rename(columns={"user.username": "user_username"})
    if "likeCount" not in df.columns and "like_count" in df.columns:
        df = df.rename(columns={"like_count": "likeCount"})
    return df


def build_bipartite_graph(df):
    """Author <-> Subreddit bipartite graph. Edge weight = sum of likeCount (if exists) else count."""
    G = nx.Graph()
    for _, row in df.iterrows():
        author = row.get("user_username")
        subreddit = row.get("subreddit")
        if pd.isna(author) or pd.isna(subreddit):
            continue
        G.add_node(author, bipartite="author")
        G.add_node(subreddit, bipartite="subreddit")
        weight = 1.0
        if "likeCount" in row and not pd.isna(row["likeCount"]):
            try:
                weight = float(row["likeCount"])
            except Exception:
                weight = 1.0
        if G.has_edge(author, subreddit):
            G[author][subreddit]["weight"] += weight
        else:
            G.add_edge(author, subreddit, weight=weight)
    return G


def project_authors(G):
    """Project bipartite graph onto authors (co-posting in same subreddit).
    Edge weight = number of shared subreddits (or summed weights)."""
    authors = [n for n, d in G.nodes(data=True) if d.get("bipartite") == "author"]
    P = nx.bipartite.weighted_projected_graph(G, authors)
    return P


def compute_metrics(G):
    metrics = {}
    metrics["n_nodes"] = G.number_of_nodes()
    metrics["n_edges"] = G.number_of_edges()
    if G.number_of_nodes() == 0:
        metrics.update({
            "avg_degree": 0, "density": 0, "avg_clustering": None,
            "avg_shortest_path": None, "n_components": 0, "largest_component": 0
        })
        return metrics

    degs = [d for _, d in G.degree()]
    metrics["avg_degree"] = float(np.mean(degs))
    metrics["density"] = float(nx.density(G))
    try:
        metrics["avg_clustering"] = float(nx.average_clustering(G))
    except Exception:
        metrics["avg_clustering"] = None
    try:
        UG = G.to_undirected()
        comps = list(nx.connected_components(UG))
        metrics["n_components"] = len(comps)
        metrics["largest_component"] = int(max(len(c) for c in comps)) if comps else 0
        if metrics["largest_component"] > 1:
            largest = UG.subgraph(max(comps, key=len))
            metrics["avg_shortest_path"] = float(nx.average_shortest_path_length(largest))
        else:
            metrics["avg_shortest_path"] = None
    except Exception:
        metrics["n_components"] = None
        metrics["largest_component"] = None
        metrics["avg_shortest_path"] = None

    # centralities (author projection assumed)
    try:
        dc = nx.degree_centrality(G)
        metrics["max_degree_centrality"] = float(max(dc.values())) if dc else 0.0
    except Exception:
        metrics["max_degree_centrality"] = None

    return metrics


def top_influencers_by_centrality(P, topk=10):
    """Return top-k authors by degree centrality and by weighted degree"""
    results = []
    if P.number_of_nodes() == 0:
        return results
    deg_cent = nx.degree_centrality(P)
    weighted_deg = {n: d for n, d in P.degree(weight="weight")}
    for n in sorted(P.nodes(), key=lambda x: deg_cent.get(x, 0), reverse=True)[:topk]:
        results.append({
            "author": n,
            "degree_centrality": float(deg_cent.get(n, 0)),
            "weighted_degree": float(weighted_deg.get(n, 0))
        })
    return results


def analyze_per_content(df):
    summary = {}
    influencers_rows = []
    # overall
    G_all = build_bipartite_graph(df)
    P_all = project_authors(G_all)
    summary["all"] = compute_metrics(P_all)
    for inf in top_influencers_by_centrality(P_all, topk=10):
        inf_row = {"category": "all", **inf}
        influencers_rows.append(inf_row)

    for ctype in sorted(df.get("content_type", pd.Series(["unknown"])).fillna("unknown").unique()):
        subdf = df[df["content_type"] == ctype]
        G = build_bipartite_graph(subdf)
        P = project_authors(G)
        summary[ctype] = compute_metrics(P)
        for inf in top_influencers_by_centrality(P, topk=10):
            inf_row = {"category": ctype, **inf}
            influencers_rows.append(inf_row)

    return summary, influencers_rows


def main():
    df = load_processed()
    if "content_type" not in df.columns:
        df["content_type"] = df.get("source_file", "").astype(str).apply(lambda x: "unknown")

    summary, influencers = analyze_per_content(df)

    # save summary
    rows = []
    for k, metrics in summary.items():
        row = {"category": k}
        row.update(metrics)
        rows.append(row)
    pd.DataFrame(rows).to_csv(OUT_SUMMARY, index=False)
    print(f"Wrote metrics summary -> {OUT_SUMMARY}")

    # save influencers
    inf_df = pd.DataFrame(influencers)
    if not inf_df.empty:
        inf_df.to_csv(OUT_INFLUENCERS, index=False)
        print(f"Wrote top influencers -> {OUT_INFLUENCERS}")
    else:
        print("No influencers to write (empty graph).")

    # print quick terminal summary
    print("\nQuick metrics summary (transposed):")
    print(pd.DataFrame(rows).set_index("category").T)

    # show top influencers per category
    if not inf_df.empty:
        print("\nTop influencers (by degree centrality) sample:")
        print(inf_df.groupby("category").head(3).reset_index(drop=True))

if __name__ == "__main__":
    main()