"""
memory_visualization.py – Cognee Knowledge Graph Visualization Page
=====================================================================
Reads the active world from Streamlit session state (shared across
pages) and passes its dataset name to visualize_graph() — which
REQUIRES an explicit dataset when Cognee Cloud access control is on.
"""

import sys
import webbrowser
from pathlib import Path

# ── Ensure project root is on sys.path ─────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
import streamlit.components.v1 as components

# ── Page config – MUST be first Streamlit call ──────────────────────
st.set_page_config(
    page_title="Memory Visualization | LoreBuilder",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    :root {
        --bg-darkest:  #111844;
        --bg-dark:     #4B5694;
        --bg-mid:      #7288AE;
        --accent:      #EAE0CF;
        --border:      rgba(234, 224, 207, 0.2);
        --text-main:   #FFFFFF;
        --text-on-accent: #000000;
    }
    .stApp {
        background: var(--bg-darkest);
        font-family: 'Inter', sans-serif;
        color: var(--text-main);
    }
    .stButton > button {
        background: var(--bg-mid) !important;
        color: var(--text-main) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: var(--bg-dark) !important;
        border-color: var(--accent) !important;
    }
    .viz-heading {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--accent);
        text-align: center;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .viz-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .info-box {
        background: var(--bg-dark);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        color: var(--text-main);
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .graph-container {
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
        background: var(--bg-mid);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-top: 1rem;
    }
    /* Full screen modifiers */
    .fs-graph-container {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        z-index: 99999 !important;
        background: var(--bg-darkest) !important;
        border-radius: 0 !important;
        border: none !important;
        padding-top: 60px !important;
    }
    .btn-fs-exit {
        position: fixed !important;
        top: 10px !important;
        right: 20px !important;
        z-index: 100000 !important;
    }
    #MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── Backend imports ──────────────────────────────────────────────────
from Backend.cognee_manager import generate_graph_visualization
from Backend.async_runner import run_async
from Backend.config import GRAPH_HTML_PATH, validate_config
from Backend.world_loader import get_world_names

# ── Navigation ──────────────────────────────────────────────────────
if st.button("← Back to World Builder", key="btn_back"):
    st.switch_page("app.py")

# ── Headings ─────────────────────────────────────────────────────────
st.markdown('<div class="viz-heading">🕸️ Memory Knowledge Graph</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="viz-subtitle">Interactive visualization of the Cognee knowledge graph — '
    'explore how world lore is stored as connected nodes and edges</div>',
    unsafe_allow_html=True,
)

# ── Config check ─────────────────────────────────────────────────────
missing = validate_config()
if missing:
    st.error(f"⚠️ Missing configuration: {', '.join(missing)}.")
    st.stop()

# ── World selector ───────────────────────────────────────────────────
# Session state carries active_world from the main page.
# Also let user pick any initialized world directly on this page.
all_worlds = get_world_names()
initialized = list(st.session_state.get("initialized_worlds", set()))

if not initialized:
    st.warning(
        "⚠️ No worlds have been initialized yet.\n\n"
        "Go back to **World Builder**, choose a world, and confirm initialization first. "
        "Then come back here to visualize its knowledge graph."
    )
    st.stop()

# Default selection: whatever world was active on main page
default_world = st.session_state.get("active_world") or initialized[0]
default_idx = initialized.index(default_world) if default_world in initialized else 0

selected_world = st.selectbox(
    "Select world to visualize",
    options=initialized,
    index=default_idx,
    key="viz_world_select",
)

# ── Session state for the HTML cache ─────────────────────────────────
# ── Session state for the HTML cache ─────────────────────────────────
if "viz_world_cached" not in st.session_state:
    st.session_state.viz_world_cached = None

# ── Controls row ─────────────────────────────────────────────────────
col_gen, col_open, col_info = st.columns([1.5, 1.5, 3])
with col_gen:
    generate_btn = st.button("🔄 Generate / Refresh", key="btn_generate_graph")
with col_open:
    # If we already have a graph generated for the selected world, allow opening it again without regenerating
    if GRAPH_HTML_PATH.exists() and st.session_state.viz_world_cached == selected_world:
        if st.button("🌐 Open Saved Graph", key="btn_open_saved"):
            webbrowser.open_new_tab(f"file:///{GRAPH_HTML_PATH.absolute()}")
with col_info:
    st.markdown("""
    <div class="info-box" style="padding: 0.6rem 1rem;">
    📌 <strong>Note:</strong> Generating or opening a graph will open it in a new browser tab.
    </div>
    """, unsafe_allow_html=True)

# ── Generate on button click ──────────────────────────────────────────
if generate_btn:
    with st.spinner(f"🧠 Fetching knowledge graph for '{selected_world}' from Cognee Cloud..."):
        try:
            html = run_async(generate_graph_visualization(selected_world))
            GRAPH_HTML_PATH.write_text(html, encoding="utf-8")
            st.session_state.viz_world_cached = selected_world
            webbrowser.open_new_tab(f"file:///{GRAPH_HTML_PATH.absolute()}")
            st.success(f"✅ Graph generated for **{selected_world}** and opened in a new tab!")
        except Exception as exc:
            st.error(f"❌ Failed to generate graph: {exc}")
            st.stop()

# ── Render ────────────────────────────────────────────────────────────
st.markdown('<div class="graph-container" style="padding: 3rem; text-align: center; color: var(--text-main);">', unsafe_allow_html=True)
st.markdown(
    f"<h3 style='margin-bottom: 1rem; color: var(--accent);'>Graph Visualization Output</h3>"
    f"<p style='font-size: 1.1rem; line-height: 1.5;'>Click the <b>Generate / Refresh</b> button above.<br>"
    f"The interactive knowledge graph for <b>{selected_world}</b> will open directly in a new browser tab.</p>",
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)
