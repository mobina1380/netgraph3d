# netgraph3d 🌐

<p align="center">
  <b>Turn any NetworkX graph into a stunning interactive 3D visualization — with one line of code.</b>
</p>

<p align="center">
  Interactive • Self-contained HTML • Zero frontend setup • Share anywhere
</p>

---

## ✨ Demo

<p align="center">
  <img src="https://github.com/mobina1380/netgraph3d/blob/main/assets/demo.gif?raw=true" width="900"/>
</p>

---

## 🚀 Quick Start

```python
from netgraph3d import to_html
import networkx as nx

G = nx.karate_club_graph()

to_html(G, title="Karate Club Network")
```

That's it.

A fully interactive 3D graph opens instantly in your browser.

No server.  
No JavaScript setup.  
No frontend framework required.

---

## 📦 Installation

```bash
pip install netgraph3d
```

---

## 🎯 Features

- 🖱️ Click any node to inspect attributes in a side panel
- 🔍 Search and highlight nodes by name or label
- 🏷️ Toggle node labels on/off
- 🔗 Toggle edge labels on/off
- 🔄 Auto-rotate the scene
- 🖱️ Drag to rotate manually
- 🔎 Smooth zoom support
- ⌨️ Press `Escape` to deselect nodes
- 📄 Export as a single self-contained HTML file
- 🌐 Share anywhere — no backend required

---

# 📚 Supported Input Formats

## NetworkX Graph

```python
import networkx as nx
from netgraph3d import to_html

G = nx.Graph()

G.add_node("Alice", role="admin", score=95)
G.add_node("Bob", role="user", score=72)

G.add_edge(
    "Alice",
    "Bob",
    weight=0.8,
    relation="colleague"
)

to_html(G, title="My Network")
```

---

## CSV Files

```python
import networkx as nx
import pandas as pd
from netgraph3d import to_html

# edges.csv columns:
# source, target, weight, relation

edges_df = pd.read_csv("edges.csv")

G = nx.from_pandas_edgelist(
    edges_df,
    source="source",
    target="target",
    edge_attr=True
)

# Optional node metadata
nodes_df = pd.read_csv("nodes.csv").set_index("id")

for node, attrs in nodes_df.to_dict(orient="index").items():
    if G.has_node(node):
        G.nodes[node].update(attrs)

to_html(G, title="CSV Network")
```

### edges.csv

```csv
source,target,weight,relation
Alice,Bob,0.8,friend
Bob,Carol,0.5,colleague
```

### nodes.csv

```csv
id,label,group
Alice,Alice,Engineering
Bob,Bob,Marketing
```

---

## Excel Files

```python
import networkx as nx
import pandas as pd
from netgraph3d import to_html

edges_df = pd.read_excel(
    "graph.xlsx",
    sheet_name="edges"
)

G = nx.from_pandas_edgelist(
    edges_df,
    source="source",
    target="target",
    edge_attr=True
)

to_html(G, title="Excel Network")
```

---

## JSON Files

```python
import networkx as nx
import json
from netgraph3d import to_html

with open("graph.json", encoding="utf-8") as f:
    data = json.load(f)

G = nx.Graph()

for n in data["nodes"]:
    nid = n["id"]
    attrs = {
        k: v
        for k, v in n.items()
        if k != "id"
    }

    G.add_node(nid, **attrs)

for e in data["edges"]:
    G.add_edge(
        e["source"],
        e["target"],
        **e.get("properties", {})
    )

to_html(G, title="JSON Network")
```

---

# 🧪 Built-in Test Graphs

Perfect for quick experimentation.

```python
import networkx as nx
from netgraph3d import to_html

# Classic social network
G = nx.karate_club_graph()

# Other options:
# G = nx.les_miserables_graph()
# G = nx.barabasi_albert_graph(50, 2)

to_html(G, title="Test Network")
```

---

# ⚙️ API Reference

```python
to_html(
    G,
    output_path="network_graph.html",
    title="3D Network Graph",
    pos_3d=None,
    seed=42,
    open_browser=True
)
```

| Parameter | Description |
|---|---|
| `G` | NetworkX graph |
| `output_path` | Output HTML file |
| `title` | Browser title |
| `pos_3d` | Optional custom node positions |
| `seed` | Layout reproducibility |
| `open_browser` | Automatically open output |

---

# 🧩 Node Attributes

```python
G.add_node(
    "Alice",
    label="Alice Smith",
    department="Engineering",
    level=3
)
```

All node attributes automatically appear in the info panel.

---

# 🔗 Edge Attributes

```python
G.add_edge(
    "Alice",
    "Bob",
    weight=0.9,
    relation="manager",
    since=2021
)
```

| Attribute | Purpose |
|---|---|
| `weight` | Edge thickness & opacity |
| `relation` / `type` | Edge label |
| other attrs | Stored and accessible |

---

# 📋 Requirements

Core:

- Python >= 3.8
- networkx

Optional:

```bash
pip install pandas openpyxl
```

---

# 📄 License

MIT License — free to use, modify, and distribute.