# 🧠 Meme–Hashtag–Misinformation Diffusion Analysis  
### Understanding how different types of content spread across online social networks

---

## 📘 Overview

This project analyzes how **memes**, **hashtags**, and **misinformation** spread differently across social networks.  
Using Reddit data, we construct and analyze diffusion networks to understand how users interact, how information propagates, and how communities form around different content types.

The project combines **data collection**, **network modeling**, **graph analytics**, and **interactive visualization** to identify key patterns and influencers in content diffusion.

---

## 🏗️ Project Structure

```
meme-diffusion-project/
├── data/
│   ├── raw/                  # Raw JSONL data from Reddit
│   └── processed/            # Cleaned CSVs, metrics, and visualizations
│
├── src/
│   ├── config.py             # Project constants and query definitions
│   ├── reddit_scrape.py      # Reddit scraper using PRAW and .env credentials
│   ├── build_network.py      # Builds bipartite and user–user graphs
│   ├── analyze.py            # Computes graph metrics and influencer data
│   ├── visualize.py          # Static visualization (Matplotlib / PyVis)
│   ├── interactive_plotly.py # Interactive Plotly-based visualization (HTML)
│   └── generate_sample_data.py # Generates synthetic data for testing
│
├── .env                      # Reddit API credentials (kept private)
├── requirements.txt           # Python dependencies
└── README.md                  # Project documentation (this file)
```

---

## 🔍 Research Question

> How do **memes**, **hashtags**, and **misinformation** spread differently in online networks?

We aim to explore:
- How large and connected these diffusion networks are.
- Whether certain content types form tighter or looser communities.
- Who the key spreaders or “influencers” are in each category.

---

## ⚙️ Implementation Details

### 1. **Data Collection**
- Platform: **Reddit**
- API: [PRAW](https://praw.readthedocs.io/en/latest/)
- Queries defined in `src/config.py` under `SCRAPE_ITEMS`
- Environment variables for API access stored in `.env` file:
  ```
  REDDIT_CLIENT_ID=xxxx
  REDDIT_CLIENT_SECRET=xxxx
  REDDIT_USERNAME=xxxx
  REDDIT_PASSWORD=xxxx
  REDDIT_USER_AGENT=DiffusionAnalysis/1.0
  ```

Each query saves:
- Raw posts → `data/raw/<topic>.jsonl`
- Cleaned data → `data/processed/<topic>_clean.csv`

---

### 2. **Data Cleaning & Preprocessing**
Each post is normalized to include:
- `id`, `date`, `content`, `user_username`, `replyCount`, `likeCount`, `subreddit`, `content_type`

Content types:
- 🟦 Meme  
- 🟧 Hashtag  
- 🔴 Misinformation  

---

### 3. **Network Construction**

We build a **bipartite network**:
- Nodes: Authors (users) and Subreddits  
- Edges: “User posted in Subreddit” (weighted by upvotes/likes)

Then we project it into an **Author–Author Network**, where:
- Nodes = Users  
- Edges = Shared subreddit participation  
- Edge weight = Strength of connection (co-participation frequency)

---

### 4. **Network Analysis Metrics**

We compute a set of **graph-theoretic metrics** using NetworkX:

| Metric | Description | Interpretation |
|--------|-------------|----------------|
| `n_nodes` | Number of nodes | Users/subreddits involved |
| `n_edges` | Number of connections | Total relationships formed |
| `avg_degree` | Average degree | How connected nodes are |
| `density` | Network density | Higher → more interactions |
| `avg_clustering` | Local clustering coefficient | Measures tight communities |
| `avg_shortest_path` | Average path length | Lower → faster spread |
| `n_components` | Number of clusters | Fragmentation of network |
| `max_degree_centrality` | Most connected node | Key influencer |
| `weighted_degree` | Sum of connection weights | Strength of influence |

Output files:
- `data/processed/graph_metrics_summary.csv`
- `data/processed/top_influencers.csv`

---

### 5. **Visualization**

#### 🖼️ Static Visualization (`src/build_network.py`)
- Uses Matplotlib to show a simplified bipartite view (authors ↔ subreddits).

#### 🌐 Interactive Visualization (`src/interactive_plotly.py`)
- Generates **interactive network graph**: `data/processed/network_plotly.html`
- Node size ∝ Influence (weighted degree)
- Node color ∝ Content type
- Hover tooltips show:
  - Username  
  - Weighted degree  
  - Number of posts  
  - Dominant content type  

Example:
```
username: u/ExampleUser
weighted_degree: 142.5
posts: 12
dominant: meme
```

Open the file in your browser to explore interactively.

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/meme-diffusion-project.git
cd meme-diffusion-project
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Add your Reddit credentials
Create a `.env` file in the project root with:
```
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
REDDIT_USERNAME=...
REDDIT_PASSWORD=...
REDDIT_USER_AGENT=DiffusionAnalysis/1.0
```

### 5. Run the pipeline
```bash
# Scrape data
python3 src/reddit_scrape.py

# Build network
python3 src/build_network.py

# Analyze network metrics
python3 src/analyze.py

# Generate interactive graph
python3 src/interactive_plotly.py
open data/processed/network_plotly.html   # macOS
```

---

## 📊 Example Outputs

| File | Description |
|------|--------------|
| `data/raw/meme_1.jsonl` | Raw scraped Reddit data |
| `data/processed/meme_1_clean.csv` | Cleaned structured CSV |
| `data/processed/graph_metrics_summary.csv` | Summary of metrics per category |
| `data/processed/top_influencers.csv` | List of top users by centrality |
| `data/processed/network_plotly.html` | Interactive diffusion graph |

---

## 💬 Key Insights (Example Findings)

| Content Type | Behavior |
|---------------|-----------|
| **Memes** | Spread rapidly, often across many communities (high degree, low clustering). |
| **Hashtags** | Bridge distinct groups, creating broader but shallower diffusion patterns. |
| **Misinformation** | Tends to form dense, closed communities (high clustering, low diversity). |

---

## 📚 Technologies Used

- **Python 3.9+**
- **Reddit API (PRAW)**
- **NetworkX** – graph construction and metrics  
- **Matplotlib** – static visualization  
- **Plotly** – interactive visualization  
- **pandas** – data wrangling  
- **dotenv** – credential management  
- **pyvis (optional)** – alternative HTML visualization  

---

## 🧠 Future Improvements

- Add **dropdown filters** for content type inside the interactive HTML.  
- Add **timeline animation** (diffusion over time).  
- Extend scraping to include **comments and reply chains** for deeper diffusion tracking.  
- Integrate with **Dash or Streamlit** for a live web dashboard.

---

## 🪪 Author

**Lakshya Mehta**  
**Khushi Bansal**
**Aziz Barwaniwala**

---

## 📄 License
This project is open source under the **MIT License**.  
Feel free to use, modify, and cite with attribution.

---

## 🧾 References
- [PRAW Reddit API Documentation](https://praw.readthedocs.io/)
- [NetworkX Documentation](https://networkx.org/)
- [Plotly Graph Objects](https://plotly.com/python/graph-objects/)
- Vosoughi, Roy, & Aral (2018). *The spread of true and false news online.* **Science**, 359(6380), 1146–1151.

---

> “The internet is not just a network of computers — it’s a network of ideas.” 🌍
