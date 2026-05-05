# netgraph3d 🌐

**Turn any NetworkX graph into a stunning interactive 3D visualization — with one line of code.**

```python
from netgraph3d import to_html
to_html(G)
```

A single HTML file is generated and opens automatically in your browser. No server needed. No dependencies beyond NetworkX.

---

## Demo

<p align="center">
  <img src="https://github.com/mobina1380/netgraph3d/blob/main/assets/demo.gif?raw=true"/>
</p>

---

## Installation

```bash
pip install netgraph3d
```

---

## Quick Start

```python
import networkx as nx
from netgraph3d import to_html

G = nx.karate_club_graph()

to_html(G, title="Karate Club Network")
```

That's it. Your browser opens with a fully interactive 3D graph.

---

## Features

- 🖱️ Click any node to inspect all its attributes in a side panel
- 🔍 Search bar to highlight nodes by name or label
- 🏷️ Toggle node labels on/off
- 🔗 Toggle edge labels on/off
- 🔄 Auto-rotate the scene (toggle on/off)
- 🖱️ Drag to rotate manually
- 🖱️ Scroll to zoom in/out
- ⌨️ Escape to deselect a node
- 📄 Self-contained HTML — one file, share anywhere

---

## Supported Input Formats

### NetworkX graph (direct)

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

### CSV file

```python
import networkx as nx
import pandas as pd
from netgraph3d import to_html

# edges.csv columns: source, target, weight, relation
edges_df = pd.read_csv("edges.csv")

G = nx.from_pandas_edgelist(
    edges_df,
    source="source",
    target="target",
    edge_attr=True
)

# Optional: load node attributes from nodes.csv
# nodes_df = pd.read_csv("nodes.csv").set_index("id")
# for node, attrs in nodes_df.to_dict(orient="index").items():
#     if G.has_node(node):
#         G.nodes[node].update(attrs)

to_html(G, title="CSV Network")
```

**edges.csv format:**

```csv
source,target,weight,relation
Alice,Bob,0.8,friend
Bob,Carol,0.5,colleague
```

---

### Excel file

```python
import networkx as nx
import pandas as pd
from netgraph3d import to_html

# graph.xlsx: sheet "edges" with columns source, target, weight, relation
edges_df = pd.read_excel("graph.xlsx", sheet_name="edges")

G = nx.from_pandas_edgelist(
    edges_df,
    source="source",
    target="target",
    edge_attr=True
)

to_html(G, title="Excel Network")
```

**graph.xlsx sheet "edges" format:**

| source | target | weight | relation |
|--------|--------|--------|----------|
| Alice  | Bob    | 0.8    | friend   |
| Bob    | Carol  | 0.5    | colleague |

---

### JSON file

```python
import networkx as nx
import json
from netgraph3d import to_html

with open("graph.json", encoding="utf-8") as f:
    data = json.load(f)

G = nx.Graph()

for n in data["nodes"]:
    nid = n["id"]
    attrs = {k: v for k, v in n.items() if k != "id"}
    G.add_node(nid, **attrs)

for e in data["edges"]:
    G.add_edge(
        e["source"],
        e["target"],
        **e.get("properties", {})
    )

to_html(G, title="JSON Network")
```

**graph.json format:**

```json
{
  "nodes": [
    {"id": "Alice", "label": "Alice", "role": "admin"},
    {"id": "Bob", "label": "Bob", "role": "user"}
  ],
  "edges": [
    {"source": "Alice", "target": "Bob", "weight": 0.8, "relation": "friend"}
  ]
}
```

---

### Built-in NetworkX graphs (great for testing)

```python
import networkx as nx
from netgraph3d import to_html

G = nx.karate_club_graph()            # 34 nodes, classic social network
# G = nx.les_miserables_graph()       # Characters from Les Misérables
# G = nx.barabasi_albert_graph(50, 2) # Random scale-free network

to_html(G, title="Test Network")
```

---

## API Reference

```python
to_html(
    G,                                 # NetworkX graph (Graph, DiGraph, etc.)
    output_path="network_graph.html",  # Path to save the HTML file
    title="3D Network Graph",          # Title shown in browser tab and top bar
    pos_3d=None,                       # Custom {node: (x, y, z)} positions (optional)
    seed=42,                           # Random seed for layout reproducibility
    open_browser=True                  # Automatically open in browser
)
```

---

## Node attributes

Any attribute added to a node is automatically displayed in the info panel when clicked:

```python
G.add_node(
    "Alice",
    label="Alice Smith",
    department="Engineering",
    level=3
)
```

The `label` attribute is used as the node's display name. All other attributes appear in the side panel.

---

## Edge attributes

```python
G.add_edge(
    "Alice",
    "Bob",
    weight=0.9,
    relation="manager",
    since=2021
)
```

- `weight` — controls edge thickness and opacity (0.0 to 1.0)
- `relation` or `type` — used as the edge label in the visualization
- All other attributes are stored and accessible

---

## Requirements

- Python >= 3.8
- networkx

Optional (for CSV/Excel input):

- pandas
- openpyxl (`pip install openpyxl`)

---

## License

MIT License — free to use, modify, and distribute.