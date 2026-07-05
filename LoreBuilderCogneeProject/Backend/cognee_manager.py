"""
cognee_manager.py – Cognee Cloud Memory Manager
=================================================
All Cognee Cloud operations are centralised here:
  • connect()     – authenticates to Cognee Cloud once per session
  • remember()    – stores world content into a named dataset
  • recall()      – retrieves context from a named dataset
  • forget()      – removes a specific dataset from Cognee memory
  • visualize()   – generates an interactive HTML graph of the knowledge graph

Each async function is self-contained so the Streamlit frontend
can call them via asyncio.run() or nest them in an async runner.

IMPORTANT: dataset_name is always the sanitised world name, ensuring
complete isolation between different worlds.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional

import cognee

from Backend.config import (
    COGNEE_API_KEY,
    COGNEE_SERVICE_URL,
    GRAPH_HTML_PATH,
)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Internal state: track whether we are already connected
# ------------------------------------------------------------------
_is_connected: bool = False


def _sanitise_dataset_name(world_name: str) -> str:
    """
    Converts a world name into a safe dataset identifier
    (lowercase, spaces → underscores, no special chars).
    Example: "Aetheria (The Shattered Skies)" → "aetheria_the_shattered_skies"
    """
    import re
    # Remove all characters except alphanumeric, spaces and underscores
    clean = re.sub(r"[^\w\s]", "", world_name)
    # Replace whitespace with underscore and lower-case
    return re.sub(r"\s+", "_", clean.strip()).lower()


# ------------------------------------------------------------------
# Connection
# ------------------------------------------------------------------
async def connect_to_cognee() -> None:
    """
    Authenticates this session with Cognee Cloud and initialises
    the local database tables that Cognee requires (e.g. for visualize_graph).

    cognee.serve() routes remember/recall/forget/improve to the Cloud.
    setup() creates the local SQLite/PGVector tables that the SDK needs
    for local operations like visualize_graph — this is what fixes:
      DatabaseNotCreatedError: Please call await setup() first.
    """
    global _is_connected
    if _is_connected:
        return
    try:
        logger.info("Connecting to Cognee Cloud at %s", COGNEE_SERVICE_URL)
        await cognee.serve(
            url=COGNEE_SERVICE_URL,
            api_key=COGNEE_API_KEY,
        )

        # Initialise local DB tables required by the SDK (e.g. visualize_graph)
        from cognee.modules.engine.operations.setup import setup as cognee_setup
        logger.info("Running cognee setup() to initialise local DB tables...")
        await cognee_setup()

        _is_connected = True
        logger.info("Cognee Cloud connection and local setup complete.")
    except Exception as exc:
        logger.error("Failed to connect/setup Cognee: %s", exc)
        raise



# ------------------------------------------------------------------
# Remember – ingest world lore into Cognee memory
# ------------------------------------------------------------------
async def remember_world(world_name: str, content: str) -> None:
    """
    Stores world lore content into Cognee Cloud under a dataset
    named after the world.  self_improvement=True is passed so
    Cognee automatically refines the graph after ingestion.

    Args:
        world_name:  Display name of the world (used for dataset key).
        content:     Raw markdown text of the world lore.
    """
    await connect_to_cognee()
    dataset = _sanitise_dataset_name(world_name)
    logger.info("remember_world: storing into dataset '%s'", dataset)
    await cognee.remember(
        data=content,
        dataset_name=dataset,
        self_improvement=True,
    )
    logger.info("remember_world: done for dataset '%s'", dataset)


# ------------------------------------------------------------------
# Recall – retrieve relevant context from Cognee memory
# ------------------------------------------------------------------
async def recall_world(world_name: str, query: str) -> str:
    """
    Retrieves relevant knowledge-graph context for the given query
    scoped to the world's dataset.

    Returns:
        A single string aggregating all retrieved memory passages.
        Returns an empty string if nothing is found.
    """
    await connect_to_cognee()
    dataset = _sanitise_dataset_name(world_name)
    logger.info("recall_world: querying dataset '%s' with: %s", dataset, query)

    results = await cognee.recall(
        query_text=query,
        datasets=[dataset],
    )

    # Flatten results into a readable context block
    if not results:
        return ""

    passages = []
    for item in results:
        # Cognee returns objects; extract text gracefully
        if isinstance(item, str):
            passages.append(item)
        elif hasattr(item, "text"):
            passages.append(item.text)
        elif hasattr(item, "content"):
            passages.append(item.content)
        else:
            passages.append(str(item))

    context = "\n\n".join(passages)
    logger.info("recall_world: retrieved %d passages", len(passages))
    return context


# ------------------------------------------------------------------
# Forget – wipe a world's dataset from Cognee Cloud memory
# ------------------------------------------------------------------
async def forget_world(world_name: str) -> None:
    """
    Removes all memory associated with the given world dataset.
    Used by the Reset World feature.
    """
    await connect_to_cognee()
    dataset = _sanitise_dataset_name(world_name)
    logger.info("forget_world: clearing dataset '%s'", dataset)
    await cognee.forget(dataset=dataset)
    logger.info("forget_world: dataset '%s' cleared", dataset)


# ------------------------------------------------------------------
# Visualize – generate interactive HTML knowledge graph
# ------------------------------------------------------------------
async def generate_graph_visualization(world_name: str) -> str:
    """
    Fetches the interactive knowledge graph HTML directly from Cognee Cloud.

    The local cognee.api.v1.visualize.visualize_graph() function does NOT
    route to the cloud, and fails with a validation error because local
    databases don't contain the cloud datasets.

    Instead, we retrieve the dataset ID from the cloud API and request
    the visualization HTML directly from the /api/v1/visualize endpoint.
    """
    await connect_to_cognee()

    dataset_name = _sanitise_dataset_name(world_name)
    output_path = str(GRAPH_HTML_PATH)
    logger.info("Requesting cloud graph visualization for dataset '%s'", dataset_name)

    from cognee.api.v1.serve.state import get_remote_client
    client = get_remote_client()
    if not client:
        raise RuntimeError("Not connected to Cognee Cloud (remote client is None).")

    try:
        session = await client._get_session()

        # 1. Get all datasets to find the UUID for our dataset_name
        async with session.get(f"{client.service_url}/api/v1/datasets/") as resp:
            if resp.status >= 400:
                raise RuntimeError(f"Failed to fetch datasets: {await resp.text()}")
            datasets = await resp.json()

        dataset_id = None
        for ds in datasets:
            if ds.get("name") == dataset_name:
                dataset_id = ds.get("id")
                break

        if not dataset_id:
            raise RuntimeError(
                f"Dataset '{dataset_name}' not found on Cognee Cloud. "
                "Ensure this world has been initialized (remember) before visualizing."
            )

        # 2. Fetch the HTML visualization using the dataset UUID
        async with session.get(
            f"{client.service_url}/api/v1/visualize",
            params={"dataset_id": dataset_id}
        ) as resp:
            if resp.status >= 400:
                raise RuntimeError(f"Cloud visualization failed ({resp.status}): {await resp.text()}")

            # The API returns the raw HTML string
            html_content = await resp.text()

        # 3. Clean up the response (strip literal JSON quotes if present)
        # Sometimes the FastAPI endpoint wraps the HTML string in JSON quotes
        if html_content.startswith('"') and html_content.endswith('"'):
            import json
            html_content = json.loads(html_content)

        if not html_content or len(html_content) < 50:
            raise RuntimeError("Received empty or invalid HTML from Cognee Cloud.")

        # Save to disk for caching
        GRAPH_HTML_PATH.write_text(html_content, encoding="utf-8")
        logger.info("Cloud graph HTML saved (%d chars) for dataset '%s'.", len(html_content), dataset_name)
        return html_content

    except Exception as exc:
        logger.error("Failed to generate cloud graph: %s", exc)
        # Fallback to local cache if network fails
        if GRAPH_HTML_PATH.exists():
            logger.info("Falling back to cached graph HTML.")
            return GRAPH_HTML_PATH.read_text(encoding="utf-8")
        raise

# ------------------------------------------------------------------
# Progress Persistence – check if world exists on Cognee Cloud
# ------------------------------------------------------------------
async def check_world_initialized_cloud(world_name: str) -> bool:
    """
    Checks if a dataset for the given world already exists in Cognee Cloud.
    This allows us to resume progress even after restarting the Streamlit app.
    """
    try:
        await connect_to_cognee()
        dataset_name = _sanitise_dataset_name(world_name)
        
        from cognee.api.v1.serve.state import get_remote_client
        client = get_remote_client()
        if not client:
            return False
            
        session = await client._get_session()
        async with session.get(f"{client.service_url}/api/v1/datasets/") as resp:
            if resp.status >= 400:
                return False
            datasets = await resp.json()
            
        for ds in datasets:
            if ds.get("name") == dataset_name:
                return True
                
        return False
    except Exception as exc:
        logger.error("Failed to check world initialization on cloud: %s", exc)
        return False
