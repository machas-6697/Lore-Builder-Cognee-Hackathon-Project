# 🌍 LoreBuilder - AI World Narrator

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41.1-FF4B4B?logo=streamlit&logoColor=white)
![Cognee](https://img.shields.io/badge/Memory-Cognee_Cloud-orange)
![LLM](https://img.shields.io/badge/LLM-Gemma_31B-blueviolet)
![Antigravity](https://img.shields.io/badge/Built_with-Antigravity-black)

**LoreBuilder** is a highly interactive web application that allows users to explore, query, and dynamically expand pre-existing fictional worlds. Powered by Large Language Models (LLMs) and **Cognee Cloud's** advanced Knowledge Graph memory, LoreBuilder grounds the AI in established lore—significantly mitigating hallucinations and driving strong narrative consistency.

*Note: This project was developed in collaboration with Antigravity, an agentic coding assistant by Google.*

*Note: This project was developed for the online hackathon The Hangover Part AI: Where's My Context?, organized by WeMakeDevs.org and sponsored by Cognee.*

---

## 📋Project Details

LoreBuilder was built to demonstrate the absolute pinnacle of persistent AI memory. Here is how we address the core details of the project:

### 1. Potential Impact
**The Problem:** Novelists, game developers, and Tabletop RPG (D&D) masters face a massive hurdle with LLMs: *Context Window Amnesia*. When building massive fictional worlds, standard LLMs forget characters, factions, and rules, resulting in continuity errors and hallucinations. Manual wiki management takes hundreds of hours.
**The Solution:** LoreBuilder unlocks scalable, persistent AI memory. It replaces manual wikis with an automated, queryable Knowledge Graph. It allows creators to build intricate worlds over time without the AI losing track of core established details. 

### 2. Creativity & Innovation
**The Innovation:** Rather than building a standard RAG chatbot that summarizes PDFs, LoreBuilder acts as a deterministic "World Narrator". It drastically mitigates LLM hallucination by grounding the AI in a strict reliance on the Knowledge Graph for answers. Furthermore, it beautifully marries *dynamic chronological chat timelines* with a *static, ever-expanding graph-vector hybrid space*, giving users both a timeline of their creativity and a web of their world's logic.

### 3. Technical Excellence
**Engineering Practices:** The project boasts a robust, highly modular backend architecture.
- **Separation of Concerns:** Distinct modules handle `cognee_manager`, `history_manager`, `world_loader`, and the `llm_client`.
- **Async Bridging:** Implements an elegant `async_runner.py` system to safely execute Cognee's asynchronous SDK methods within Streamlit's inherently synchronous execution model.
- **Local Persistence:** Chat history seamlessly persists to localized JSON files that survive server reboots and automatically purge when a world is reset.

### 4. Best Use of Cognee
LoreBuilder leans heavily on Cognee’s advanced memory lifecycles and hybrid memory layer:
- **Memory Lifecycle APIs:** Deeply integrates `cognee.remember()` (for ingesting baseline world markdown files and new user updates, enabling `self_improvement=True`), `cognee.recall()` (for high-accuracy graph-vector context retrieval before the LLM answers), and `cognee.forget()` (for explicit graph wiping during world resets).
- **Graph Visualization:** Proves a deep understanding of the Cognee Cloud ecosystem by bypassing standard Streamlit constraints. It asynchronously queries the Cognee Cloud REST API (via `aiohttp` to `/api/v1/visualize`) to fetch the raw HTML graph visualization payload, opening it directly into a stunning, interactive, fullscreen browser tab.

### 5. User Experience
**Polish & Adoption:** The application features a breathtaking, premium UI/UX design.
- **Custom Theming:** We injected deep CSS overrides to create a professional, minimal Navy/Cream color palette, ditching the standard "Streamlit look".
- **WhatsApp-Style Chat:** A familiar, deeply intuitive chat history page with right/left aligned bubbles, scrollable containers, and one-click JSON backups.
- **Intelligent State Management:** Dropdowns and session states remember exactly what world you are working on, flawlessly persisting state data even as you navigate between the World Builder, Chat History, and Graph Visualizer pages.

---

## 🔭 Future Scope
While LoreBuilder is currently a robust single-user worldbuilding tool, the architecture lays the groundwork for several realistic, high-impact features in the future:
- **Multi-Agent Collaboration:** Implementing specialized sub-agents (e.g., a "Culture Agent" and a "Combat Agent") that independently query and update the same Cognee Knowledge Graph to flesh out different aspects of the world simultaneously.
- **Knowledge Graph to Wiki Export:** Utilizing Cognee's traversal APIs to programmatically read the entire graph state and compile it into a downloadable, structured PDF or Markdown wiki.
- **Timeline Rollbacks:** Transitioning from the current "hard reset to baseline" feature to a version-controlled graph, allowing creators to undo their last few updates if the story takes a turn they dislike.
- **Multiplayer Worldbuilding:** Upgrading the frontend to support user authentication, allowing D&D groups or co-authors to connect to the same Cognee dataset and build the world collaboratively in real-time.

## ✨ System Features

### 🧠 Cognee Knowledge Graph Integration
- **Persistent Cloud Memory:** Initializes and loads world lore directly into your Cognee Cloud tenant.
- **Strict Retrieval-Augmented Generation (RAG):** The AI answers questions and generates new story elements *strictly* based on the facts stored in the knowledge graph.
- **State Retention:** Seamlessly remembers your progress across sessions. Choose to continue your existing world or wipe the memory and start fresh.

### 🕸️ Interactive Memory Visualization
- **Graph Viewer:** Visually explore how world entities, characters, and factions are connected. 
- **Direct Cloud Fetching:** Bypasses local constraints by asynchronously querying the Cognee REST API to fetch the raw HTML knowledge graph.
- **New Tab Rendering:** Opens a stunning, interactive, and draggable knowledge graph directly in a full-screen browser tab for maximum readability.

### 💬 Persistent Chat History
- **Chronological Timelines:** All interactions ("Ask Question" or "Update World") are saved sequentially to per-world JSON files.
- **WhatsApp-Style UI:** A clean, professional, scrollable chat interface styled in a custom Navy/Cream theme.
- **Export Data:** Instantly download any world's chat history as a raw JSON backup.

---

## 🏗️ Project Architecture

```text
LoreBuilderCogneeProject/
│
├── app.py                            # Main Streamlit Application (World Builder)
├── pages/
│   ├── memory_visualization.py       # Knowledge Graph Generation & Viewer
│   └── chat_history.py               # WhatsApp-style Chat History UI
│
├── Backend/
│   ├── cognee_manager.py             # Cognee SDK & Cloud REST API integration
│   ├── llm_client.py                 # OpenRouter/Venice LLM API communication
│   ├── history_manager.py            # Local JSON chat history read/write/clear
│   ├── world_loader.py               # Parses base .md world files
│   ├── config.py                     # Environment variable validation
│   └── async_runner.py               # Async/Sync Streamlit bridge loop handling
│
├── AppData/
│   └── history/                      # Generated JSON chat logs (e.g., Eldoria.json)
│
└── .env.example                      # Template for API Keys & Credentials
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- An active [OpenRouter](https://openrouter.ai/) API key for the LLM.
- A [Cognee Cloud](https://cognee.ai/) account with Access Control enabled.

### 2. Installation
Clone the repository and install the required dependencies:
```bash
git clone https://github.com/machas-6697/Lore-Builder-Cognee-Hackathon-Project.git
cd LoreBuilderCogneeProject
pip install -r requirements.txt
```
*(Ensure `streamlit`, `cognee`, and `aiohttp` are installed)*

### 3. Environment Setup
Inside `.env`, ensure you fill in your credentials such as the following are set:
```ini
LLM_API_KEY=your_openrouter_api_key
COGNEE_API_KEY=your_cognee_cloud_key
# ... other required Cognee DB credentials
```

### 4. Run the Application
Launch the Streamlit server:
```bash
streamlit run app.py
```
The app will automatically open in your default web browser.

---

## 💡 How to Use
1. **Choose a World:** Open the left sidebar to read the raw baseline lore of 8 pre-built fictional worlds.
2. **Initialize:** Select a world from the main dropdown. The app will check Cognee Cloud for existing progress. Choose to **Start Fresh** or **Continue**.
3. **Ask & Update:** 
   - Select **❓ Ask Question** to query the AI on existing lore.
   - Select **✏️ Update World** to propose new characters, factions, or story events. The AI will generate consistent additions and permanently save them to Cognee memory.
4. **Visualize:** Navigate to the **Memory Visualization** page to see how your new additions link to the baseline lore in a node-edge graph.
5. **Review History:** Navigate to the **Chat History** page to review your chronological journey.

---

## 🛠️ Built With
- **[Streamlit](https://streamlit.io/)** - The fastest way to build data apps.
- **[Cognee](https://github.com/topoteretes/cognee)** - Scalable, deterministic Knowledge Graph memory for AI agents.
- **Python's `aiohttp`** - For seamless, non-blocking REST API calls.
