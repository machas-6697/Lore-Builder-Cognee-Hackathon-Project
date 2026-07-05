import json
import os
from pathlib import Path

# The directory where history files will be stored
HISTORY_DIR = Path("AppData/history")

def _get_file_path(world_name: str) -> Path:
    return HISTORY_DIR / f"{world_name}.json"

def _ensure_dir():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def save_interaction(world_name: str, action_type: str, prompt: str, answer: str):
    """
    Appends a new interaction to the world's chat history JSON file.
    """
    _ensure_dir()
    file_path = _get_file_path(world_name)
    
    history = []
    if file_path.exists():
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass  # If file is corrupt or unreadable, start fresh
            
    interaction = {
        "action": action_type,
        "prompt": prompt,
        "answer": answer
    }
    history.append(interaction)
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4, ensure_ascii=False)

def get_history(world_name: str) -> list:
    """
    Returns the chat history for a given world as a list of dictionaries.
    """
    file_path = _get_file_path(world_name)
    if not file_path.exists():
        return []
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def clear_history(world_name: str):
    """
    Deletes the chat history JSON file for a given world.
    """
    file_path = _get_file_path(world_name)
    if file_path.exists():
        try:
            os.remove(file_path)
        except OSError:
            pass
