"""
async_runner.py – Safe Asyncio Bridge for Streamlit
=====================================================
ROOT CAUSE OF "Event loop is closed" ERROR:
  asyncio.run() creates a NEW event loop, runs the coroutine,
  then CLOSES the loop when done. Cognee internally stores references
  to asyncio objects (connections, tasks) from the FIRST loop.
  On the next call, asyncio.run() creates a NEW loop — but Cognee's
  internal state still points to the old, now-CLOSED loop → crash.

THE FIX:
  A single persistent event loop runs forever in a daemon background
  thread. It never closes. All coroutines from Streamlit are submitted
  to this one loop via asyncio.run_coroutine_threadsafe(), which is
  thread-safe and returns a concurrent.futures.Future.

  This means Cognee always operates on the SAME event loop for the
  entire lifetime of the Streamlit process — no more closed loop errors.

Usage:
    from Backend.async_runner import run_async
    result = run_async(some_async_function(arg1, arg2))
"""

import asyncio
import threading
import logging
from typing import Any, Coroutine

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Single persistent event loop in a background daemon thread.
# This loop is created ONCE when this module is first imported
# and runs forever — it is NEVER closed.
# ------------------------------------------------------------------
_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
_thread: threading.Thread = threading.Thread(
    target=_loop.run_forever,
    name="cognee-async-loop",
    daemon=True,   # Daemon thread: auto-exits when the main process exits
)
_thread.start()
logger.debug("Persistent async event loop started in background thread.")


# ------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------
def run_async(coro: Coroutine, timeout: float = 300.0) -> Any:
    """
    Submits a coroutine to the persistent background event loop
    and blocks the calling (Streamlit) thread until the result is ready.

    Args:
        coro:    An awaitable coroutine object.
        timeout: Maximum seconds to wait (default 5 minutes for
                 long Cognee operations like remember/recall).

    Returns:
        The return value of the coroutine.

    Raises:
        Any exception raised inside the coroutine is re-raised here.
        TimeoutError if the coroutine exceeds the timeout.
    """
    if not _thread.is_alive():
        raise RuntimeError(
            "The background async event loop thread has died unexpectedly. "
            "Please restart the Streamlit application."
        )

    # Submit the coroutine to the persistent loop (thread-safe)
    future = asyncio.run_coroutine_threadsafe(coro, _loop)

    try:
        # Block the Streamlit thread until the coroutine finishes
        return future.result(timeout=timeout)
    except TimeoutError:
        future.cancel()
        raise TimeoutError(
            f"Cognee operation timed out after {timeout}s. "
            "This may happen with very large datasets or slow network."
        )
