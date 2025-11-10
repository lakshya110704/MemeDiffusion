# src/interactive_plotly.py
"""
Interactive network visualization using Plotly (produces a standalone HTML file).
- Selects top_k authors by weighted degree from the author-author projection.
- Draws edges as thin lines and nodes as scatter points with hover tooltips.
- Writes HTML to data/processed/network_plotly.html
"""

import sys
from pathlib import Path
import math
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

# ensure project root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import PROC_DIR

OUT_HTML = Path(PROC_DIR) / "network_plotly.html"

def load_processed_df():
    csvs = list(Path(PROC_DIR).glob("*_clean.csv"))
    if not csvs:
        raise SystemExit("No processed CSVs found. Run scraping step first.")
    dfs = []
    for p in csvs:
        df = pd.read_csv(p)
        df['source_file'] = p.name
        dfs.append(df)
    df = pd.concat(dfs, ignore_index=True)
    # normalize keys
    if "user_username" not in df.columns and "user.username" in df.columns:
        df = df.rename(columns={"user.username": "user_username"})
    if "likeCount" not in df.columns and "like_count" in df.columns:
        df = df.rename(columns={"like_count": "likeCount"})
    df["content_type"] = df.get("content_type", df.get("type", "unknown")).fillna("unknown")
    return df

def build_author_projection(df):
    # build bipartite author-sub graph and project to authors
    B = nx.Graph()
    for _, row in df.iterrows():
        a = row.get("user_username")
        s = row.get("subreddit")
        if pd.isna(a) or pd.isna(s):
            continue
        if not B.has_node(a):
            B.add_node(a, bipartite='author')
        if not B.has_node(s):
            B.add_node(s, bipartite='subreddit')
        w = 1.0
        if 'likeCount' in row and not pd.isna(row['likeCount']):
            try:
                w = float(row['likeCount'])
            except Exception:
                w = 1.0
        if B.has_edge(a, s):
            B[a][s]['weight'] += w
        else:
            B.add_edge(a, s, weight=w)
    authors = [n for n,d in B.nodes(data=True) if d.get('bipartite') == 'author']
    if not authors:
        return nx.Graph()
    P = nx.bipartite.weighted_projected_graph(B, authors)
    return P

def make_plot(top_k=150):
    df = load_processed_df()
    P = build_author_projection(df)
    if P.number_of_nodes() == 0:
        print("Author projection empty.")
        return

    # compute weighted degree and keep top_k
    wdeg = dict(P.degree(weight='weight'))
    top_nodes = sorted(wdeg.items(), key=lambda x: x[1], reverse=True)[:top_k]
    top_set = {n for n,_ in top_nodes}
    subP = P.subgraph(top_set).copy()

    # layout (force-directed). Use spring_layout for positions
    pos = nx.spring_layout(subP, k=0.5, iterations=200, seed=42)

    # prepare edge traces
    edge_x = []
    edge_y = []
    for u, v, d in subP.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    # edge trace (single trace)
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.6, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    # node traces
    node_x = []
    node_y = []
    texts = []
    sizes = []
    colors = []
    # compute dominant content_type per author
    dominant = df.groupby(['user_username','content_type']).size().reset_index(name='cnt')
    dominant = dominant.loc[dominant.groupby('user_username')['cnt'].idxmax()].set_index('user_username')['content_type'].to_dict()
    posts_count = df.groupby('user_username').size().to_dict()

    for n in subP.nodes():
        x,y = pos[n]
        node_x.append(x)
        node_y.append(y)
        degw = wdeg.get(n, 0.0)
        sz = 8 + math.log1p(degw) * 8
        sizes.append(sz)
        ctype = dominant.get(n, 'unknown')
        cmap = {
            'meme': '#1f77b4', 'hashtag': '#ff7f0e',
            'misinformation': '#d62728', 'unknown':'#2ca02c'
        }
        colors.append(cmap.get(ctype, '#7f7f7f'))
        texts.append(f"{n}<br>weighted_degree: {degw:.1f}<br>posts: {posts_count.get(n,0)}<br>dominant: {ctype}")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=texts,
        marker=dict(
            # colors is a list of color strings; Plotly will accept this
            color=colors,
            size=sizes,
            line=dict(width=1, color='#333')
        )
    )

    # Use a compatible layout: set title as dict instead of titlefont
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(text='Interactive diffusion network (Plotly)', x=0.5),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=50),
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                    ))
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUT_HTML), auto_open=False)
    print("Wrote interactive Plotly HTML to:", OUT_HTML)

if __name__ == '__main__':
    make_plot(top_k=150)