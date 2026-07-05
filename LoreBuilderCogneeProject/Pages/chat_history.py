import sys
import json
import html
from pathlib import Path

# ── Ensure project root is on sys.path ─────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st
from Backend.history_manager import get_history, _get_file_path
from Backend.world_loader import get_world_names

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chat History | LoreBuilder",
    page_icon="💬",
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
    
    /* Headers */
    .history-heading {
        font-family: 'Inter', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--accent);
        text-align: center;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .history-subtitle {
        text-align: center;
        color: rgba(255, 255, 255, 0.8);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    
    /* Buttons */
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
    
    /* Dropdown */
    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-mid) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-main) !important;
        border-radius: 8px !important;
    }
    
    /* Chat Container */
    .chat-showcase {
        border: 2px solid var(--accent);
        border-radius: 12px;
        background: rgba(75, 86, 148, 0.15); /* very dark translucent */
        padding: 1.5rem;
        height: 60vh;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
        margin-bottom: 1.5rem;
        scrollbar-width: thin;
        scrollbar-color: var(--accent) transparent;
    }
    .chat-showcase::-webkit-scrollbar { width: 6px; }
    .chat-showcase::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }
    
    /* Chat Bubbles */
    .chat-row {
        display: flex;
        width: 100%;
    }
    .chat-row-user {
        justify-content: flex-end;
    }
    .chat-row-ai {
        justify-content: flex-start;
    }
    .chat-bubble {
        max-width: 75%;
        padding: 1rem 1.2rem;
        border-radius: 16px;
        font-size: 0.95rem;
        line-height: 1.5;
        white-space: pre-wrap;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .bubble-user {
        background-color: var(--accent);
        color: var(--text-on-accent);
        border-bottom-right-radius: 4px;
    }
    .bubble-ai {
        background-color: var(--bg-mid);
        color: var(--text-main);
        border-bottom-left-radius: 4px;
        border: 1px solid var(--border);
    }
    .chat-action-tag {
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
        opacity: 0.7;
    }
    
    #MainMenu{visibility:hidden;}footer{visibility:hidden;}header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ── Navigation ──────────────────────────────────────────────────────
if st.button("← Back to World Builder", key="btn_back"):
    st.switch_page("app.py")

# ── Headings ─────────────────────────────────────────────────────────
st.markdown('<div class="history-heading">💬 Chat History</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="history-subtitle">Review your past conversations and lore updates for any world</div>',
    unsafe_allow_html=True,
)

# ── World selector ───────────────────────────────────────────────────
all_worlds = get_world_names()
initialized = list(st.session_state.get("initialized_worlds", set()))

if not initialized:
    st.warning(
        "⚠️ No worlds have been initialized yet.\n\n"
        "Go back to **World Builder**, choose a world, and confirm initialization first."
    )
    st.stop()

default_world = st.session_state.get("active_world") or initialized[0]
default_idx = initialized.index(default_world) if default_world in initialized else 0

selected_world = st.selectbox(
    "Select world to view history",
    options=initialized,
    index=default_idx,
    key="history_world_select",
)

# ── Fetch History ────────────────────────────────────────────────────
history_data = get_history(selected_world)

# ── Chat Showcase Render ─────────────────────────────────────────────
if not history_data:
    st.info(f"No chat history found for **{selected_world}** yet. Start interacting with the AI on the World Builder page!")
else:
    # Build HTML for WhatsApp style chat
    chat_html = '<div class="chat-showcase">\n'
    
    for item in history_data:
        action = html.escape(item.get("action", "Interaction"))
        prompt = html.escape(item.get("prompt", "")).replace('\n', '<br>')
        answer = html.escape(item.get("answer", "")).replace('\n', '<br>')
        
        # User Prompt Bubble (Right)
        chat_html += f'<div class="chat-row chat-row-user">\n'
        chat_html += f'<div class="chat-bubble bubble-user">\n'
        chat_html += f'<div class="chat-action-tag">YOU • {action}</div>\n'
        chat_html += f'{prompt}\n'
        chat_html += f'</div>\n'
        chat_html += f'</div>\n'
        
        # AI Answer Bubble (Left)
        chat_html += f'<div class="chat-row chat-row-ai">\n'
        chat_html += f'<div class="chat-bubble bubble-ai">\n'
        chat_html += f'<div class="chat-action-tag">AI • LOREBUILDER</div>\n'
        chat_html += f'{answer}\n'
        chat_html += f'</div>\n'
        chat_html += f'</div>\n'
        
    chat_html += '</div>'
    
    # Render chat HTML
    st.markdown(chat_html, unsafe_allow_html=True)
    
    # ── Download JSON Button ─────────────────────────────────────────
    json_path = _get_file_path(selected_world)
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            json_content = f.read()
            
        st.download_button(
            label=f"⬇️ Download {selected_world} History (JSON)",
            data=json_content,
            file_name=f"{selected_world}_chat_history.json",
            mime="application/json",
            use_container_width=True
        )
