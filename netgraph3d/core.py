"""
netgraph3d - Interactive 3D Network Graph Visualizer
Convert any NetworkX graph to a stunning interactive 3D HTML visualization.
"""

import json
import os
import webbrowser
import math
import random
from pathlib import Path


def _layout_3d(G, seed=42):
    """Generate 3D positions using force-directed-like placement."""
    random.seed(seed)
    nodes = list(G.nodes())
    n = len(nodes)
    
    # Try to use spring layout from networkx projected to 3D
    try:
        import networkx as nx
        pos2d = nx.spring_layout(G, seed=seed, k=2/math.sqrt(n) if n > 1 else 1)
        positions = {}
        for node in nodes:
            x, y = pos2d[node]
            z = random.uniform(-0.5, 0.5)
            positions[node] = (round(x, 4), round(y, 4), round(z, 4))
        return positions
    except Exception:
        return {node: (
            round(random.uniform(-1, 1), 4),
            round(random.uniform(-1, 1), 4),
            round(random.uniform(-1, 1), 4)
        ) for node in nodes}


def _graph_to_json(G, pos_3d=None, seed=42):
    """Convert NetworkX graph to JSON-serializable dict."""
    if pos_3d is None:
        pos_3d = _layout_3d(G, seed=seed)
    
    nodes = []
    for node in G.nodes():
        attrs = dict(G.nodes[node])
        label = attrs.pop("label", str(node))
        x, y, z = pos_3d.get(node, (0, 0, 0))
        nodes.append({
            "id": str(node),
            "label": str(label),
            "x": x,
            "y": y,
            "z": z,
            "properties": attrs
        })
    
    edges = []
    for u, v, attrs in G.edges(data=True):
        edges.append({
            "source": str(u),
            "target": str(v),
            "properties": dict(attrs)
        })
    
    return {"nodes": nodes, "edges": edges}


def _build_html(graph_data, title="3D Network Graph", bg_color="#050510"):
    """Embed graph data into a self-contained HTML file."""
    graph_json = json.dumps(graph_data, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Inter:wght@300;400;600&display=swap');

  * {{ margin: 0; padding: 0; box-sizing: border-box; }}

  body {{
    background: {bg_color};
    overflow: hidden;
    font-family: 'Inter', sans-serif;
    color: #e0e0ff;
    user-select: none;
  }}

  #canvas-container {{ position: fixed; inset: 0; }}

  /* ── Top bar ── */
  #topbar {{
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 52px;
    background: rgba(5,5,20,0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(100,120,255,0.2);
    display: flex;
    align-items: center;
    padding: 0 20px;
    gap: 16px;
    z-index: 200;
  }}

  #topbar h1 {{
    font-family: 'Space Mono', monospace;
    font-size: 14px;
    color: #7b93ff;
    letter-spacing: 2px;
    text-transform: uppercase;
    flex: 1;
  }}

  .ctrl-btn {{
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 6px 14px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 6px;
    color: #b0b8e8;
    font-size: 12px;
    font-family: 'Space Mono', monospace;
    cursor: pointer;
    transition: all .2s;
  }}
  .ctrl-btn:hover {{ background: rgba(100,120,255,0.15); border-color: rgba(100,120,255,0.4); color: #fff; }}
  .ctrl-btn.active {{ background: rgba(100,120,255,0.25); border-color: #6478ff; color: #a0b0ff; }}

  .dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #6478ff;
    box-shadow: 0 0 6px #6478ff;
    transition: background .2s;
  }}
  .ctrl-btn.active .dot {{ background: #4cff9e; box-shadow: 0 0 6px #4cff9e; }}

  /* ── Stats ── */
  #stats {{
    position: fixed;
    bottom: 20px; left: 20px;
    background: rgba(5,5,20,0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(100,120,255,0.2);
    border-radius: 10px;
    padding: 12px 18px;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #6478ff;
    z-index: 200;
    line-height: 1.8;
  }}
  #stats span {{ color: #a0c0ff; }}

  /* ── Info panel ── */
  #info-panel {{
    position: fixed;
    top: 70px; right: 20px;
    width: 280px;
    background: rgba(5,5,20,0.9);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(100,120,255,0.25);
    border-radius: 12px;
    padding: 0;
    z-index: 200;
    transform: translateX(320px);
    transition: transform .35s cubic-bezier(.4,0,.2,1);
    overflow: hidden;
  }}
  #info-panel.visible {{ transform: translateX(0); }}

  #panel-header {{
    padding: 14px 18px;
    background: rgba(100,120,255,0.1);
    border-bottom: 1px solid rgba(100,120,255,0.15);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  #panel-header h2 {{
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: #7b93ff;
    letter-spacing: 1px;
  }}
  #panel-close {{
    width: 24px; height: 24px;
    background: rgba(255,255,255,0.06);
    border: none;
    border-radius: 4px;
    color: #7b93ff;
    cursor: pointer;
    font-size: 14px;
    display: flex; align-items: center; justify-content: center;
    transition: background .2s;
  }}
  #panel-close:hover {{ background: rgba(255,80,80,0.2); color: #ff6060; }}

  #panel-body {{ padding: 16px 18px; }}

  #node-id {{
    font-family: 'Space Mono', monospace;
    font-size: 20px;
    color: #ffffff;
    margin-bottom: 4px;
  }}
  #node-label {{
    font-size: 12px;
    color: #7080b0;
    margin-bottom: 16px;
    font-style: italic;
  }}

  .prop-row {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    gap: 10px;
  }}
  .prop-row:last-child {{ border-bottom: none; }}
  .prop-key {{
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #5060a0;
    text-transform: uppercase;
    letter-spacing: 1px;
    white-space: nowrap;
  }}
  .prop-val {{
    font-size: 12px;
    color: #c0d0ff;
    text-align: right;
    word-break: break-word;
  }}
  .prop-val.number {{ color: #4cff9e; font-family: 'Space Mono', monospace; }}
  .prop-val.important {{ color: #ff9e4c; font-weight: 600; }}

  /* ── Connections list ── */
  #conn-section {{
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid rgba(100,120,255,0.15);
  }}
  #conn-section h3 {{
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #5060a0;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }}
  .conn-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
    font-size: 12px;
    color: #8898cc;
  }}
  .conn-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }}

  /* ── Tooltip ── */
  #tooltip {{
    position: fixed;
    pointer-events: none;
    background: rgba(5,5,20,0.92);
    border: 1px solid rgba(100,120,255,0.35);
    border-radius: 7px;
    padding: 7px 12px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #c0d0ff;
    z-index: 300;
    opacity: 0;
    transition: opacity .15s;
    white-space: nowrap;
    transform: translate(14px, -50%);
  }}

  /* ── Help ── */
  #help {{
    position: fixed;
    bottom: 20px; right: 20px;
    background: rgba(5,5,20,0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(100,120,255,0.2);
    border-radius: 10px;
    padding: 12px 18px;
    font-size: 11px;
    color: #5060a0;
    z-index: 200;
    line-height: 2;
  }}
  #help span {{ color: #7080b0; }}

  /* ── Search ── */
  #search-wrap {{
    position: fixed;
    top: 70px; left: 20px;
    z-index: 200;
  }}
  #search {{
    background: rgba(5,5,20,0.85);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(100,120,255,0.2);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    font-family: 'Space Mono', monospace;
    color: #c0d0ff;
    width: 200px;
    outline: none;
    transition: border-color .2s;
  }}
  #search::placeholder {{ color: #3a4070; }}
  #search:focus {{ border-color: rgba(100,120,255,0.5); }}
</style>
</head>
<body>

<div id="canvas-container"></div>

<div id="topbar">
  <h1>⬡ {title}</h1>
  <button class="ctrl-btn active" id="btn-node-labels" onclick="toggleNodeLabels()">
    <div class="dot" id="dot-nl"></div> Node Labels
  </button>
  <button class="ctrl-btn active" id="btn-edge-labels" onclick="toggleEdgeLabels()">
    <div class="dot" id="dot-el"></div> Edge Labels
  </button>
  <button class="ctrl-btn active" id="btn-rotate" onclick="toggleRotate()">
    <div class="dot" id="dot-rot"></div> Auto-Rotate
  </button>
</div>

<div id="search-wrap">
  <input id="search" type="text" placeholder="Search node..." oninput="onSearch(this.value)">
</div>

<div id="stats">
  Nodes <span id="stat-nodes">0</span> &nbsp;|&nbsp; Edges <span id="stat-edges">0</span>
</div>

<div id="help">
  <span>Drag</span> to rotate &nbsp;|&nbsp; <span>Scroll</span> to zoom<br>
  <span>Click</span> node for details &nbsp;|&nbsp; <span>Esc</span> to deselect
</div>

<div id="info-panel">
  <div id="panel-header">
    <h2 id="panel-title">NODE INFO</h2>
    <button id="panel-close" onclick="closePanel()">✕</button>
  </div>
  <div id="panel-body">
    <div id="node-id"></div>
    <div id="node-label"></div>
    <div id="node-props"></div>
    <div id="conn-section">
      <h3>Connections</h3>
      <div id="conn-list"></div>
    </div>
  </div>
</div>

<div id="tooltip"></div>

<script>
// ── DATA ──────────────────────────────────────────────────────────────────
const GRAPH_DATA = {graph_json};

// ── STATE ─────────────────────────────────────────────────────────────────
let showNodeLabels = true;
let showEdgeLabels = true;
let autoRotate = true;
let selectedNodeId = null;
let hoveredNodeId = null;

// ── THREE SETUP ──────────────────────────────────────────────────────────
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x050510, 0.022);

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 500);
camera.position.set(0, 0, 22);

const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
document.getElementById('canvas-container').appendChild(renderer.domElement);

// Lights
scene.add(new THREE.AmbientLight(0x8090ff, 0.6));
const pLight = new THREE.PointLight(0x6090ff, 2, 80);
pLight.position.set(10, 10, 10);
scene.add(pLight);
const pLight2 = new THREE.PointLight(0xff6090, 1.2, 60);
pLight2.position.set(-10, -8, -5);
scene.add(pLight2);

// ── ORBIT CONTROLS (manual) ───────────────────────────────────────────────
let isDragging = false;
let prevMouse = {{x:0, y:0}};
let spherical = {{theta: 0, phi: Math.PI/2, radius: 22}};
const pivot = new THREE.Group();
scene.add(pivot);

renderer.domElement.addEventListener('mousedown', e => {{ isDragging = true; prevMouse = {{x: e.clientX, y: e.clientY}}; }});
window.addEventListener('mouseup', () => isDragging = false);
window.addEventListener('mousemove', e => {{
  if (isDragging) {{
    const dx = e.clientX - prevMouse.x;
    const dy = e.clientY - prevMouse.y;
    spherical.theta -= dx * 0.007;
    spherical.phi = Math.max(0.1, Math.min(Math.PI - 0.1, spherical.phi + dy * 0.007));
    prevMouse = {{x: e.clientX, y: e.clientY}};
  }}
}});
window.addEventListener('wheel', e => {{
  spherical.radius = Math.max(5, Math.min(80, spherical.radius + e.deltaY * 0.05));
}});

function updateCamera() {{
  camera.position.set(
    spherical.radius * Math.sin(spherical.phi) * Math.sin(spherical.theta),
    spherical.radius * Math.cos(spherical.phi),
    spherical.radius * Math.sin(spherical.phi) * Math.cos(spherical.theta)
  );
  camera.lookAt(0, 0, 0);
}}

// ── BUILD GRAPH ───────────────────────────────────────────────────────────
const nodeMeshes = {{}};
const nodeMap = {{}};
const edgeMeshes = [];
const labelSprites = {{}};
const edgeLabelSprites = [];

// Color palette by category / type
const palette = ['#4cff9e','#6478ff','#ff9e4c','#ff4c9e','#4cdfff','#d4ff4c','#c04cff','#ff6060'];
const nodeColorMap = {{}};

function makeSprite(text, color='#c0d0ff', size=48) {{
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  const fontSize = size;
  ctx.font = `bold ${{fontSize}}px Space Mono, monospace`;
  const w = ctx.measureText(text).width + 24;
  canvas.width = w; canvas.height = fontSize + 16;
  ctx.font = `bold ${{fontSize}}px Space Mono, monospace`;
  ctx.fillStyle = color + 'cc';
  ctx.fillText(text, 12, fontSize + 2);
  const tex = new THREE.CanvasTexture(canvas);
  const mat = new THREE.SpriteMaterial({{ map: tex, transparent: true, depthTest: false }});
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(canvas.width / 80, canvas.height / 80, 1);
  return sprite;
}}

// Build nodes
GRAPH_DATA.nodes.forEach((node, i) => {{
  nodeMap[node.id] = node;
  const color = palette[i % palette.length];
  nodeColorMap[node.id] = color;

  const geo = new THREE.SphereGeometry(0.22, 32, 32);
  const mat = new THREE.MeshStandardMaterial({{
    color: new THREE.Color(color),
    roughness: 0.2,
    metalness: 0.8,
    emissive: new THREE.Color(color),
    emissiveIntensity: 0.15
  }});
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(node.x * 9, node.y * 9, node.z * 9);
  mesh.userData = {{ nodeId: node.id }};
  pivot.add(mesh);
  nodeMeshes[node.id] = mesh;

  // Glow ring
  const ringGeo = new THREE.RingGeometry(0.26, 0.35, 32);
  const ringMat = new THREE.MeshBasicMaterial({{
    color: new THREE.Color(color), side: THREE.DoubleSide,
    transparent: true, opacity: 0.3, depthTest: false
  }});
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.userData.isRing = true;
  mesh.add(ring);

  // Label
  const sprite = makeSprite(node.label || node.id, color);
  sprite.position.set(mesh.position.x, mesh.position.y + 0.55, mesh.position.z);
  sprite.userData = {{ nodeId: node.id, isLabel: true }};
  pivot.add(sprite);
  labelSprites[node.id] = sprite;
}});

// Build edges
GRAPH_DATA.edges.forEach(edge => {{
  const src = nodeMeshes[edge.source];
  const tgt = nodeMeshes[edge.target];
  if (!src || !tgt) return;

  const srcPos = src.position;
  const tgtPos = tgt.position;

  // Tube for edge
  const dir = new THREE.Vector3().subVectors(tgtPos, srcPos);
  const len = dir.length();
  const mid = new THREE.Vector3().addVectors(srcPos, tgtPos).multiplyScalar(0.5);
  
  const curve = new THREE.CatmullRomCurve3([
    srcPos.clone(),
    mid.clone().add(new THREE.Vector3(
      (Math.random()-0.5)*0.4,
      (Math.random()-0.5)*0.4,
      (Math.random()-0.5)*0.4
    )),
    tgtPos.clone()
  ]);

  const geo = new THREE.TubeGeometry(curve, 12, 0.018, 6, false);
  const weight = edge.properties.weight || 0.5;
  const opacity = 0.25 + weight * 0.5;
  const mat = new THREE.MeshBasicMaterial({{
    color: 0x4466cc,
    transparent: true,
    opacity: opacity
  }});
  const tube = new THREE.Mesh(geo, mat);
  tube.userData = {{ edgeData: edge }};
  pivot.add(tube);
  edgeMeshes.push(tube);

  // Edge label
  const props = edge.properties;
  const labelText = props.relation || props.type || props.label || '';
  if (labelText) {{
    const sprite = makeSprite(labelText, '#5060a0', 32);
    sprite.position.copy(mid);
    sprite.userData = {{ isEdgeLabel: true }};
    pivot.add(sprite);
    edgeLabelSprites.push(sprite);
  }}
}});

// ── STATS ─────────────────────────────────────────────────────────────────
document.getElementById('stat-nodes').textContent = GRAPH_DATA.nodes.length;
document.getElementById('stat-edges').textContent = GRAPH_DATA.edges.length;

// ── RAYCASTING ────────────────────────────────────────────────────────────
const raycaster = new THREE.Raycaster();
raycaster.params.Mesh.threshold = 0.3;
const mouse = new THREE.Vector2();
const tooltip = document.getElementById('tooltip');

function getNodeMeshes() {{ return Object.values(nodeMeshes); }}

window.addEventListener('mousemove', e => {{
  if (isDragging) {{ tooltip.style.opacity = '0'; return; }}
  mouse.x = (e.clientX / innerWidth) * 2 - 1;
  mouse.y = -(e.clientY / innerHeight) * 2 + 1;

  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(getNodeMeshes());

  if (hits.length > 0) {{
    const mesh = hits[0].object;
    const nid = mesh.userData.nodeId;
    if (nid !== hoveredNodeId) {{
      if (hoveredNodeId && hoveredNodeId !== selectedNodeId) resetNodeScale(hoveredNodeId);
      hoveredNodeId = nid;
      if (nid !== selectedNodeId) pulseNode(nid, 1.5);
    }}
    const node = nodeMap[nid];
    tooltip.textContent = node.label || nid;
    tooltip.style.left = e.clientX + 'px';
    tooltip.style.top = e.clientY + 'px';
    tooltip.style.opacity = '1';
    renderer.domElement.style.cursor = 'pointer';
  }} else {{
    if (hoveredNodeId && hoveredNodeId !== selectedNodeId) resetNodeScale(hoveredNodeId);
    hoveredNodeId = null;
    tooltip.style.opacity = '0';
    renderer.domElement.style.cursor = 'default';
  }}
}});

renderer.domElement.addEventListener('click', e => {{
  if (isDragging) return;
  raycaster.setFromCamera(mouse, camera);
  const hits = raycaster.intersectObjects(getNodeMeshes());
  if (hits.length > 0) {{
    const nid = hits[0].object.userData.nodeId;
    selectNode(nid);
  }} else {{
    closePanel();
  }}
}});

window.addEventListener('keydown', e => {{ if (e.key === 'Escape') closePanel(); }});

// ── NODE SELECTION ────────────────────────────────────────────────────────
function pulseNode(nid, scale) {{
  const mesh = nodeMeshes[nid];
  if (mesh) mesh.scale.setScalar(scale);
}}
function resetNodeScale(nid) {{
  const mesh = nodeMeshes[nid];
  if (mesh) mesh.scale.setScalar(1);
}}

function selectNode(nid) {{
  if (selectedNodeId) resetNodeScale(selectedNodeId);
  selectedNodeId = nid;
  pulseNode(nid, 2.2);
  highlightConnected(nid);
  showPanel(nid);
}}

function highlightConnected(nid) {{
  // Dim all edges, brighten connected
  edgeMeshes.forEach(tube => {{
    const e = tube.userData.edgeData;
    const connected = (e.source === nid || e.target === nid);
    tube.material.opacity = connected ? 0.9 : 0.08;
    tube.material.color.setHex(connected ? 0x4cff9e : 0x223355);
  }});
  // Dim non-connected nodes
  Object.entries(nodeMeshes).forEach(([id, mesh]) => {{
    if (id === nid) return;
    const isNeighbor = GRAPH_DATA.edges.some(e =>
      (e.source === nid && e.target === id) ||
      (e.target === nid && e.source === id)
    );
    mesh.material.emissiveIntensity = isNeighbor ? 0.4 : 0.02;
    mesh.material.opacity = isNeighbor ? 1 : 0.3;
    mesh.material.transparent = !isNeighbor;
  }});
}}

function resetHighlight() {{
  edgeMeshes.forEach(tube => {{
    const w = tube.userData.edgeData?.properties?.weight || 0.5;
    tube.material.opacity = 0.25 + w * 0.5;
    tube.material.color.setHex(0x4466cc);
  }});
  Object.values(nodeMeshes).forEach(mesh => {{
    mesh.material.emissiveIntensity = 0.15;
    mesh.material.transparent = false;
  }});
}}

function showPanel(nid) {{
  const node = nodeMap[nid];
  document.getElementById('node-id').textContent = node.id;
  document.getElementById('node-label').textContent = node.label !== node.id ? node.label : '';
  
  const propsDiv = document.getElementById('node-props');
  propsDiv.innerHTML = '';
  Object.entries(node.properties || {{}}).forEach(([k, v]) => {{
    const row = document.createElement('div');
    row.className = 'prop-row';
    const valClass = typeof v === 'number' ? 'number' : (v === 'important' ? 'important' : '');
    row.innerHTML = `<span class="prop-key">${{k}}</span><span class="prop-val ${{valClass}}">${{v}}</span>`;
    propsDiv.appendChild(row);
  }});

  const connList = document.getElementById('conn-list');
  connList.innerHTML = '';
  GRAPH_DATA.edges.forEach(e => {{
    const other = e.source === nid ? e.target : e.target === nid ? e.source : null;
    if (!other) return;
    const otherNode = nodeMap[other];
    const color = nodeColorMap[other] || '#6478ff';
    const item = document.createElement('div');
    item.className = 'conn-item';
    const rel = e.properties.relation || e.properties.type || '';
    item.innerHTML = `<div class="conn-dot" style="background:${{color}};box-shadow:0 0 5px ${{color}}"></div>
      <span style="color:${{color}};cursor:pointer" onclick="selectNode('${{other}}')">${{otherNode?.label || other}}</span>
      ${{rel ? `<span style="color:#3a4070;font-size:10px;margin-left:4px">(${{rel}})</span>` : ''}}`;
    connList.appendChild(item);
  }});

  document.getElementById('info-panel').classList.add('visible');
}}

function closePanel() {{
  document.getElementById('info-panel').classList.remove('visible');
  if (selectedNodeId) resetNodeScale(selectedNodeId);
  selectedNodeId = null;
  resetHighlight();
}}

// ── TOGGLE CONTROLS ───────────────────────────────────────────────────────
function toggleNodeLabels() {{
  showNodeLabels = !showNodeLabels;
  Object.values(labelSprites).forEach(s => s.visible = showNodeLabels);
  const btn = document.getElementById('btn-node-labels');
  btn.classList.toggle('active', showNodeLabels);
}}

function toggleEdgeLabels() {{
  showEdgeLabels = !showEdgeLabels;
  edgeLabelSprites.forEach(s => s.visible = showEdgeLabels);
  const btn = document.getElementById('btn-edge-labels');
  btn.classList.toggle('active', showEdgeLabels);
}}

function toggleRotate() {{
  autoRotate = !autoRotate;
  const btn = document.getElementById('btn-rotate');
  btn.classList.toggle('active', autoRotate);
}}

// ── SEARCH ────────────────────────────────────────────────────────────────
function onSearch(val) {{
  const q = val.toLowerCase().trim();
  if (!q) {{ resetHighlight(); return; }}
  Object.entries(nodeMap).forEach(([id, node]) => {{
    const match = id.toLowerCase().includes(q) || (node.label||'').toLowerCase().includes(q);
    const mesh = nodeMeshes[id];
    mesh.material.emissiveIntensity = match ? 0.6 : 0.02;
    mesh.material.transparent = !match;
    mesh.material.opacity = match ? 1 : 0.15;
    mesh.scale.setScalar(match ? 1.8 : 1);
  }});
}}

// ── ANIMATE ───────────────────────────────────────────────────────────────
let t = 0;
function animate() {{
  requestAnimationFrame(animate);
  t += 0.016;

  if (autoRotate && !isDragging) {{
    spherical.theta += 0.003;
  }}
  updateCamera();

  // Labels always face camera
  Object.values(labelSprites).forEach(s => s.quaternion.copy(camera.quaternion));
  edgeLabelSprites.forEach(s => s.quaternion.copy(camera.quaternion));

  // Gentle ring rotation
  pivot.traverse(obj => {{
    if (obj.userData.isRing) {{
      obj.rotation.z = t * 0.8;
      obj.rotation.x = t * 0.3;
    }}
  }});

  renderer.render(scene, camera);
}}

animate();

window.addEventListener('resize', () => {{
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
}});
</script>
</body>
</html>"""
    return html


def to_html(G, output_path=None, title="3D Network Graph",
            pos_3d=None, seed=42, open_browser=True):
    """
    Convert a NetworkX graph G to a self-contained interactive 3D HTML file.

    Parameters
    ----------
    G : networkx.Graph or DiGraph
        The input graph. Node attributes like 'label', and edge attributes
        like 'weight', 'relation', 'type' are automatically visualized.
    output_path : str or Path, optional
        Path to save the HTML file. Defaults to 'network_graph.html'.
    title : str
        Title shown in the browser tab and top bar.
    pos_3d : dict, optional
        Custom {node: (x, y, z)} positions. If None, auto-computed.
    seed : int
        Random seed for layout reproducibility.
    open_browser : bool
        If True, automatically opens the HTML in the default browser.

    Returns
    -------
    str : Path to the saved HTML file.
    """
    if output_path is None:
        output_path = "network_graph.html"
    output_path = str(output_path)

    graph_data = _graph_to_json(G, pos_3d=pos_3d, seed=seed)
    html_content = _build_html(graph_data, title=title)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    abs_path = os.path.abspath(output_path)
    n_nodes = len(graph_data["nodes"])
    n_edges = len(graph_data["edges"])

    print(f"✅  Graph exported: {abs_path}")
    print(f"    Nodes: {n_nodes}  |  Edges: {n_edges}")

    if open_browser:
        webbrowser.open(f"file:///{abs_path}")
        print("🌐  Opening in browser...")

    return abs_path
