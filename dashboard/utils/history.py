"""
History persistence utilities for the dashboard.
Saves simulation history to disk so it persists across sessions.
"""
import json
from pathlib import Path
from datetime import datetime


HISTORY_FILE = Path(__file__).parent / "data" / "history.json"


def load_history() -> list:
    """Load simulation history from disk."""
    if not HISTORY_FILE.exists():
        return []
    
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: list):
    """Save simulation history to disk."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def add_history_entry(entry: dict):
    """Add a new entry to history and save to disk."""
    history = load_history()
    history.append(entry)
    save_history(history)
    return history


def clear_history():
    """Clear all history entries."""
    save_history([])
