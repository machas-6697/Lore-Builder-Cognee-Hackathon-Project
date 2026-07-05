"""
app.py is the LoreBuilder Main Application
=======================================
Entry point for the Streamlit application.
"""

import sys
import os
from pathlib import Path

# ── Ensure project root is importable ──────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

# ── Page config – This will be the first Streamlit call ──────────────────────
st.set_page_config(
    page_title="LoreBuilder | AI World Narrator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Backend imports ─────────────────────────────────────────────────
from Backend.config import validate_config
from Backend.world_loader import get_world_names, get_world_content
from Backend.cognee_manager import (
    remember_world,
    recall_world,
    forget_world,
    check_world_initialized_cloud
)
from Backend.llm_client import ask_question, generate_world_update
from Backend.async_runner import run_async
from Backend.history_manager import save_interaction, clear_history

# ══════════════════════════════════════════════════════════════════
# GLOBAL CSS – Theme & Layout
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── CSS Variables ── */
:root {
    --bg-darkest:  #111844;
    --bg-dark:     #4B5694;
    --bg-mid:      #7288AE;
    --accent:      #EAE0CF;
    --accent-dim:  rgba(234, 224, 207, 0.25);
    --border:      rgba(234, 224, 207, 0.2);
    --text-main:   #FFFFFF;
    --text-on-accent: #000000;
}

/* ── App background ── */
.stApp {
    background: var(--bg-darkest);
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
    min-height: 100vh;
}

/* ── Remove default Streamlit padding ── */
.block-container {
    padding-top: 1rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
    max-width: 100% !important;
}

/* ══════════════════════════════
   SIDEBAR
══════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-dark) !important;
    border-right: 1px solid var(--border) !important;
    width: 20vw !important;
    min-width: 240px !important;
    max-width: 320px !important;
}

[data-testid="stSidebar"] * {
    color: var(--text-main) !important;
}

/* Sidebar header */
.sidebar-title {
    font-family: 'Inter', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--accent);
    text-align: center;
    padding: 1rem 0 0.5rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.sidebar-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 0.5rem 0 1rem;
}

/* Sidebar select box */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: var(--bg-mid) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 8px !important;
}

/* Sidebar lore text area */
.lore-display-box {
    background: var(--bg-mid);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    margin-top: 1rem;
    font-size: 0.85rem;
    line-height: 1.6;
    color: var(--text-main);
    max-height: 55vh;
    overflow-y: auto;
    white-space: pre-wrap;
    scrollbar-width: thin;
    scrollbar-color: var(--accent) transparent;
}

.lore-display-box::-webkit-scrollbar { width: 4px; }
.lore-display-box::-webkit-scrollbar-track { background: transparent; }
.lore-display-box::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 2px; }

/* ══════════════════════════════
   MAIN HEADINGS
══════════════════════════════ */
.main-heading {
    font-family: 'Inter', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--accent);
    text-align: center;
    letter-spacing: 1px;
    margin-bottom: 0;
    line-height: 1.1;
    padding-top: 0.5rem;
}

.sub-heading {
    font-family: 'Inter', sans-serif;
    font-size: 1.05rem;
    font-weight: 400;
    color: rgba(255, 255, 255, 0.8);
    text-align: center;
    margin-top: 1.5rem;
    margin-bottom: 1.2rem;
}

/* ══════════════════════════════
   CONTROL ROW (dropdowns + buttons)
══════════════════════════════ */
/* Dropdown */
[data-testid="stSelectbox"] > div > div {
    background: var(--bg-mid) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 8px !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stSelectbox"] > div > div:hover {
    border-color: var(--accent) !important;
    box-shadow: 0 0 8px var(--accent-dim) !important;
}

/* ── Generic button reset ── */
.stButton > button {
    background: var(--bg-mid) !important;
    color: var(--text-main) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    padding: 0.55rem 1.2rem !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    background: var(--bg-dark) !important;
    border-color: var(--accent) !important;
}

/* ── Active (highlighted) action button ── */
.action-btn-active > button {
    background: var(--accent) !important;
    border-color: var(--accent) !important;
    color: var(--text-on-accent) !important; /* TEXT ON LIGHT BACKGROUND MUST BE BLACK */
    font-weight: 700 !important;
}

/* ══════════════════════════════
   CHAT AREA
══════════════════════════════ */
/* Chat input */
[data-testid="stTextArea"] textarea {
    background: var(--bg-mid) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-main) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    resize: vertical !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stTextArea"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 8px var(--border-dim) !important;
    outline: none !important;
}

/* ── Response / output box ── */
.response-box {
    background: var(--bg-mid);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.2rem 1.5rem;
    margin-top: 1rem;
    color: var(--text-light);
    line-height: 1.75;
    font-size: 0.95rem;
    min-height: 60px;
    white-space: pre-wrap;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* ── Status message boxes ── */
.status-box {
    background: var(--bg-dark);
    border: 1px solid var(--accent);
    border-radius: 8px;
    padding: 1rem 1.5rem;
    color: var(--text-light);
    font-style: italic;
    text-align: center;
    margin-top: 0.8rem;
}

.done-box {
    background: #e8f5e9;
    border: 1px solid #4caf50;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    color: #2e7d32;
    text-align: center;
    font-weight: 500;
    margin-top: 0.8rem;
}

/* ══════════════════════════════
   FEATURES SECTION
══════════════════════════════ */
.features-container {
    border-top: 1px solid var(--border);
    padding-top: 1rem;
    margin-top: 0.5rem;
}

.features-heading {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    letter-spacing: 2px;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 0.6rem;
    font-weight: 600;
}

/* ══════════════════════════════
   SCROLLBAR GLOBAL
══════════════════════════════ */
* { scrollbar-width: thin; scrollbar-color: var(--accent) transparent; }
*::-webkit-scrollbar { width: 5px; }
*::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }

/* ── Hide Streamlit branding ── */
#MainMenu { visibility: hidden; }
footer     { visibility: hidden; }
header     { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
# SESSION STATE INITIALISATION
# ══════════════════════════════════════════════════════════════════
def _init_state():
    defaults = {
        "active_world":        None,     # Currently selected world name
        "world_initialized":   False,    # Has the active world been pushed to Cognee?
        "active_action":       None,     # "ask" | "update" | "reset" | None
        "chat_response":       "",       # Latest LLM response text
        "status_message":      "",       # Transient status text
        "status_type":         "",       # "loading" | "done" | "error" | ""
        "show_init_popup":     False,    # Show world-init confirmation popup?
        "show_action_warning": False,    # Show "select an action" warning popup?
        "show_reset_popup":    False,    # Show reset-in-progress popup?
        "show_info_popup":     False,    # Show feature info popup?
        "pending_world":       None,     # World chosen but not yet confirmed
        "initialized_worlds":  set(),    # Set of worlds already pushed to Cognee
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

_init_state()


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
def _world_names() -> list[str]:
    return get_world_names()


def _set_action(action: str):
    """Toggle action button selection. Re-clicking the active one deselects it."""
    if st.session_state.active_action == action:
        st.session_state.active_action = None
    else:
        st.session_state.active_action = action


# ══════════════════════════════════════════════════════════════════
# LEFT SIDEBAR
# ══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-title">⚔ WORLDS</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    world_names = _world_names()

    sidebar_world = st.selectbox(
        "Choose a world to preview",
        options=["— Select a World —"] + world_names,
        key="sidebar_world_select",
        label_visibility="collapsed",
    )

    if sidebar_world and sidebar_world != "— Select a World —":
        try:
            lore_text = get_world_content(sidebar_world)
            st.markdown(
                f'<div class="lore-display-box">{lore_text}</div>',
                unsafe_allow_html=True,
            )
        except FileNotFoundError:
            st.error("World file not found.")

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    if st.button("💬 Chat History", use_container_width=True):
        st.switch_page("pages/chat_history.py")


# ══════════════════════════════════════════════════════════════════
# CONFIG VALIDATION BANNER
# ══════════════════════════════════════════════════════════════════
missing_cfg = validate_config()
if missing_cfg:
    st.warning(
        f"⚠️ Missing environment variables: **{', '.join(missing_cfg)}**. "
        "Copy `.env.example` to `.env` and fill in your credentials.",
        icon="⚙️",
    )


# ══════════════════════════════════════════════════════════════════
# MAIN CONTENT AREA
# We use a single column that fills the space beside the sidebar.
# ══════════════════════════════════════════════════════════════════

# ── Section proportions using st.container + flex ──────────────────
chat_container = st.container()
features_container = st.container()

# ──────────────────────────────────────────────────────────────────
# AI CHAT SECTION  (80% of page height via CSS)
# ──────────────────────────────────────────────────────────────────
with chat_container:
    # ── Main heading ──
    st.markdown('<div class="main-heading">Lore Builder</div>', unsafe_allow_html=True)

    # ── Vertical gap + sub-heading ──
    st.markdown('<div style="height:2rem"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-heading">'
        'Chat with AI to build your own story in a world by choosing any one of the 8 pre existing worlds'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Control row: Choose World dropdown + 3 action buttons ──
    col_world, col_ask, col_update, col_reset = st.columns([3, 1.4, 1.4, 1.4])

    with col_world:
        default_world_idx = 0
        if st.session_state.active_world in world_names:
            default_world_idx = world_names.index(st.session_state.active_world) + 1

        chosen_world = st.selectbox(
            "Choose World",
            options=["— Choose World —"] + world_names,
            index=default_world_idx,
            key="main_world_select",
            label_visibility="visible",
        )

    # ── Action buttons with highlighted state ──────────────────────
    ask_active    = st.session_state.active_action == "ask"
    update_active = st.session_state.active_action == "update"
    reset_active  = st.session_state.active_action == "reset"

    with col_ask:
        ask_class = "action-btn-active" if ask_active else ""
        st.markdown(f'<div class="{ask_class}">', unsafe_allow_html=True)
        st.markdown(
            '<div title="Used to ask question on existing world knowledge">',
            unsafe_allow_html=True,
        )
        if st.button(
            "❓ Ask Question" + (" ✓" if ask_active else ""),
            key="btn_ask",
            help="Used to ask question on existing world knowledge",
        ):
            _set_action("ask")
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

    with col_update:
        update_class = "action-btn-active" if update_active else ""
        st.markdown(f'<div class="{update_class}">', unsafe_allow_html=True)
        st.markdown(
            '<div title="Used to update the world lore with new content">',
            unsafe_allow_html=True,
        )
        if st.button(
            "✏️ Update World" + (" ✓" if update_active else ""),
            key="btn_update",
            help="Used to update the world lore with new content",
        ):
            _set_action("update")
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

    with col_reset:
        reset_class = "action-btn-active" if reset_active else ""
        st.markdown(f'<div class="{reset_class}">', unsafe_allow_html=True)
        st.markdown(
            '<div title="Used to reset the world environment to its original state">',
            unsafe_allow_html=True,
        )
        if st.button(
            "🔄 Reset World" + (" ✓" if reset_active else ""),
            key="btn_reset",
            help="Used to reset the world environment to its original state",
        ):
            _set_action("reset")
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

    # ── World initialisation popup trigger ─────────────────────────
    if (
        chosen_world != "— Choose World —"
        and chosen_world != st.session_state.active_world
    ):
        st.session_state.pending_world = chosen_world
        st.session_state.show_init_popup = True

    @st.dialog("🌍 Initialize World?")
    def world_init_dialog(pending):
        # Check cloud if we haven't already checked for this pending world
        if "cloud_check_done_for" not in st.session_state or st.session_state.cloud_check_done_for != pending:
            with st.spinner("Checking Cognee Cloud for saved progress..."):
                has_cloud_data = run_async(check_world_initialized_cloud(pending))
                st.session_state.has_cloud_data = has_cloud_data
                st.session_state.cloud_check_done_for = pending
        
        has_cloud_data = st.session_state.get("has_cloud_data", False)

        if has_cloud_data:
            st.info(f"Saved progress found for **{pending}** in Cognee Cloud!")
            st.markdown("Would you like to continue with your saved progress, or delete it and start fresh?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Continue with Existing Progress", use_container_width=True):
                    st.session_state.show_init_popup = False
                    st.session_state.active_world = pending
                    st.session_state.world_initialized = True
                    st.session_state.initialized_worlds.add(pending)
                    st.session_state.chat_response = ""
                    st.session_state.active_action = None
                    st.session_state.status_type = "done"
                    st.session_state.status_message = "✅ Loaded from Cloud. You are ready to go!"
                    st.rerun()
            with col2:
                if st.button("Delete Progress & Start Fresh", type="primary", use_container_width=True):
                    st.session_state.show_init_popup = False
                    st.session_state.active_world = pending
                    st.session_state.world_initialized = False
                    st.session_state.chat_response = ""
                    st.session_state.active_action = None
                    st.session_state.status_type = "loading_fresh"
                    st.session_state.status_message = "🌀 Wiping cloud memory and starting fresh..."
                    st.rerun()
        else:
            st.markdown(f"Shall the world **{pending}** be initialized?\nThis will load its lore into Cognee memory so you can interact with it.")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm", use_container_width=True):
                    st.session_state.show_init_popup = False
                    st.session_state.active_world = pending
                    st.session_state.world_initialized = False
                    st.session_state.chat_response = ""
                    st.session_state.active_action = None
                    if pending in st.session_state.initialized_worlds:
                        st.session_state.world_initialized = True
                        st.session_state.status_type = "done"
                        st.session_state.status_message = "✅ Done! You are ready to go! (World already in memory)"
                    else:
                        st.session_state.status_type = "loading"
                        st.session_state.status_message = "🌀 The world is currently being initialized. Please wait . . ."
                    st.rerun()
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.show_init_popup = False
                    st.session_state.pending_world = None
                    st.rerun()

    # ── POPUP: World Initialisation Confirmation ───────────────────
    if st.session_state.show_init_popup and st.session_state.pending_world:
        world_init_dialog(st.session_state.pending_world)

    # ── PERFORM WORLD INITIALIZATION (if loading state is set) ─────
    if (
        st.session_state.status_type in ("loading", "loading_fresh")
        and st.session_state.active_world
    ):
        st.markdown(
            f'<div class="status-box">🌀 {st.session_state.status_message}</div>',
            unsafe_allow_html=True,
        )
        with st.spinner("Loading world lore into Cognee Cloud..."):
            try:
                world_content = get_world_content(st.session_state.active_world)
                if st.session_state.status_type == "loading_fresh":
                    run_async(forget_world(st.session_state.active_world))
                run_async(remember_world(st.session_state.active_world, world_content))
                st.session_state.initialized_worlds.add(st.session_state.active_world)
                st.session_state.world_initialized = True
                st.session_state.status_type = "done"
                st.session_state.status_message = "✅ Done! You are ready to go!"
                st.rerun()
            except Exception as exc:
                st.session_state.status_type = "error"
                st.session_state.status_message = f"❌ Initialization failed: {exc}"
                st.rerun()

    # ── Status display ─────────────────────────────────────────────
    if st.session_state.status_type == "loading":
        st.markdown(
            f'<div class="status-box">{st.session_state.status_message}</div>',
            unsafe_allow_html=True,
        )
    elif st.session_state.status_type == "done":
        st.markdown(
            f'<div class="done-box">{st.session_state.status_message}</div>',
            unsafe_allow_html=True,
        )
    elif st.session_state.status_type == "error":
        st.error(st.session_state.status_message)

    st.markdown('<div style="height:0.8rem"></div>', unsafe_allow_html=True)

    # ── Chat input ─────────────────────────────────────────────────
    user_prompt = st.text_area(
        "Your prompt",
        placeholder=(
            "Type your question or story update here…\n"
            "(Select an action button above first)"
        ),
        height=110,
        key="chat_input",
        label_visibility="collapsed",
    )

    # ── Submit button ──────────────────────────────────────────────
    col_spacer, col_submit = st.columns([5, 1])
    with col_submit:
        submit_clicked = st.button("▶ Submit", key="btn_submit")

    # ── POPUP: No action selected warning ─────────────────────────
    if st.session_state.show_action_warning:
        st.markdown(
            """
            <div style="
                background: rgba(200,60,0,0.2);
                border: 1px solid rgba(200,60,0,0.7);
                border-radius: 12px;
                padding: 1rem 1.5rem;
                color: #ffaa88;
                text-align: center;
                margin: 0.5rem 0;
            ">
                ⚠️ <strong>You must select any one of the three buttons</strong>
                which signifies the action to be taken on your prompt onto Cognee memory.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("✖ Dismiss", key="btn_dismiss_warning"):
            st.session_state.show_action_warning = False
            st.rerun()

    # ── POPUP: Reset World in Progress ────────────────────────────
    if st.session_state.show_reset_popup:
        st.markdown(
            """
            <div class="status-box">
                🔄 World getting reset to original state . . . . . .
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── HANDLE SUBMIT ──────────────────────────────────────────────
    if submit_clicked:
        st.session_state.show_action_warning = False

        # Guard: world must be initialized
        if not st.session_state.world_initialized or not st.session_state.active_world:
            st.error(
                "⚠️ Please choose and initialize a world first "
                "before submitting a prompt."
            )

        # Guard: action button must be selected
        elif st.session_state.active_action is None:
            st.session_state.show_action_warning = True
            st.rerun()

        # Guard: prompt must not be empty
        elif not user_prompt.strip():
            st.warning("✏️ Please enter a prompt before submitting.")

        # ── ASK QUESTION ─────────────────────────────────────────
        elif st.session_state.active_action == "ask":
            with st.spinner("🔍 Recalling world knowledge from Cognee..."):
                try:
                    world_context = run_async(
                        recall_world(st.session_state.active_world, user_prompt)
                    )
                    with st.spinner("🤖 LLM is crafting your answer..."):
                        answer = ask_question(world_context, user_prompt)
                    st.session_state.chat_response = answer
                    save_interaction(st.session_state.active_world, "Ask Question", user_prompt, answer)
                    st.session_state.active_action = None  # Unhighlight button
                    st.rerun()
                except Exception as exc:
                    st.error(f"❌ Error during Ask: {exc}")
                    st.session_state.active_action = None
                    st.rerun()

        # ── UPDATE WORLD ──────────────────────────────────────────
        elif st.session_state.active_action == "update":
            with st.spinner("📖 Fetching existing world context from Cognee..."):
                try:
                    world_context = run_async(
                        recall_world(st.session_state.active_world, user_prompt)
                    )
                    with st.spinner("✍️ LLM is generating new lore..."):
                        new_lore = generate_world_update(world_context, user_prompt)
                    with st.spinner("💾 Saving new lore to Cognee memory..."):
                        run_async(
                            remember_world(st.session_state.active_world, new_lore)
                        )
                    st.session_state.chat_response = (
                        f"✅ **World Updated!**\n\n"
                        f"The following new lore has been added to **{st.session_state.active_world}**:\n\n"
                        f"---\n\n{new_lore}"
                    )
                    save_interaction(st.session_state.active_world, "Update World", user_prompt, new_lore)
                    st.session_state.active_action = None
                    st.rerun()
                except Exception as exc:
                    st.error(f"❌ Error during Update: {exc}")
                    st.session_state.active_action = None
                    st.rerun()

        # ── RESET WORLD ───────────────────────────────────────────
        elif st.session_state.active_action == "reset":
            st.session_state.show_reset_popup = True
            st.rerun()

    # ── Execute RESET (if reset popup is active) ───────────────────
    if st.session_state.show_reset_popup and st.session_state.active_world:
        try:
            # Step 1: forget
            run_async(forget_world(st.session_state.active_world))
            # Step 2: re-ingest original lore
            original_content = get_world_content(st.session_state.active_world)
            run_async(remember_world(st.session_state.active_world, original_content))
            # Step 3: cleanup state
            clear_history(st.session_state.active_world)
            st.session_state.show_reset_popup = False
            st.session_state.active_action = None
            st.session_state.chat_response = (
                f"🔄 **{st.session_state.active_world}** has been reset to its original lore."
            )
            st.rerun()
        except Exception as exc:
            st.session_state.show_reset_popup = False
            st.session_state.active_action = None
            st.error(f"❌ Reset failed: {exc}")
            st.rerun()

    # ── Response output window ──────────────────────────────────────
    if st.session_state.chat_response:
        st.markdown(
            f'<div class="response-box">{st.session_state.chat_response}</div>',
            unsafe_allow_html=True,
        )


# ──────────────────────────────────────────────────────────────────
# FEATURES SECTION  (20% of page height)
# ──────────────────────────────────────────────────────────────────
with features_container:
    st.markdown('<div class="features-container">', unsafe_allow_html=True)
    st.markdown('<div class="features-heading">⚙ Features</div>', unsafe_allow_html=True)

    col_mem_viz, col_info_btn, col_spacer2 = st.columns([2, 2, 5])

    with col_mem_viz:
        if st.button("🕸️ Memory Visualization", key="btn_mem_viz"):
            st.switch_page("pages/memory_visualization.py")

    with col_info_btn:
        if st.button("❓ Info on Features", key="btn_info"):
            st.session_state.show_info_popup = True
            st.rerun()

    # ── Info popup ─────────────────────────────────────────────────
    @st.dialog("Feature Guide")
    def feature_guide_dialog():
        st.markdown(
            """
            **🌍 Choose World**
            Select one of the 8 pre-existing fictional worlds. After confirming, the world's 
            lore is loaded into Cognee Cloud memory — your AI's long-term brain for that world.
            
            ---
            
            **❓ Ask Question**
            Ask the AI anything about the selected world. The AI *strictly* answers 
            from Cognee memory — no hallucinations, only established lore facts.
            
            ---
            
            **✏️ Update World**
            Add new story elements, factions, characters, or events. The AI generates 
            lore consistent with the existing world and saves it into Cognee memory.
            
            ---
            
            **🔄 Reset World**
            Wipes all updates from Cognee memory and restores the world to its original 
            state from the source `.md` file.
            
            ---
            
            **🕸️ Memory Visualization**
            Opens an interactive knowledge graph showing how all lore entities and their 
            relationships are stored in Cognee — nodes, edges, and connections at a glance.
            
            ---
            
            **💬 Chat History**
            View a WhatsApp-style timeline of all your questions and lore updates for the current world.
            
            ---
            
            **📌 Worlds Sidebar**
            Use the left sidebar dropdown to preview the raw lore of any world at any time.
            """
        )
        if st.button("Close", use_container_width=True):
            st.session_state.show_info_popup = False
            st.rerun()

    if st.session_state.show_info_popup:
        feature_guide_dialog()

    st.markdown('</div>', unsafe_allow_html=True)
