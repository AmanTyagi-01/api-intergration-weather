"""
history_manager.py
==================
Manages the persistent search history stored in data/history.json.
Supports saving, loading, displaying, and filtering past weather lookups.

Author  : Weather Intelligence Dashboard
Version : 1.0.0
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

HISTORY_FILE  = os.path.join("data", "history.json")
MAX_HISTORY   = 50          # Cap the file at 50 entries to avoid unbounded growth



def save_to_history(weather_data: dict) -> bool:
    """
    Append a weather result to the JSON history file.

    Parameters
    ----------
    weather_data : dict – Parsed weather dictionary from weather_api.py

    Returns
    -------
    bool – True on success, False on failure
    """
    try:
        history = load_history()

        record = {
            "search_id":   len(history) + 1,
            "searched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "city":        weather_data.get("city", ""),
            "country":     weather_data.get("country", ""),
            "temperature": weather_data.get("temperature", 0),
            "condition":   weather_data.get("condition", ""),
            "description": weather_data.get("description", ""),
            "humidity":    weather_data.get("humidity", 0),
            "wind_speed":  weather_data.get("wind_speed", 0),
            "rain_1h":     weather_data.get("rain_1h", 0.0),
        }

        history.append(record)

        if len(history) > MAX_HISTORY:
            history = history[-MAX_HISTORY:]

        _write_history(history)
        logger.info(f"Saved search #{record['search_id']} for '{record['city']}' to history.")
        return True

    except Exception as exc:
        logger.exception(f"Failed to save history entry: {exc}")
        return False


def load_history() -> list:
    """
    Load and return the full search history from disk.

    Returns
    -------
    list – List of history dicts; empty list if file missing / corrupt
    """
    if not os.path.exists(HISTORY_FILE):
        logger.debug("History file not found; returning empty list.")
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if not isinstance(data, list):
                logger.warning("History file has unexpected format; resetting.")
                return []
            return data

    except json.JSONDecodeError as err:
        logger.warning(f"History JSON is corrupt ({err}); returning empty list.")
        return []

    except OSError as err:
        logger.error(f"Could not read history file: {err}")
        return []


def clear_history() -> bool:
    """
    Wipe all search history from disk.

    Returns
    -------
    bool – True on success
    """
    try:
        _write_history([])
        logger.info("Search history cleared by user.")
        print("\n  ✅  Search history cleared successfully.\n")
        return True
    except Exception as exc:
        logger.exception(f"Failed to clear history: {exc}")
        print(f"\n  ❌  Could not clear history: {exc}\n")
        return False



def display_history(limit: int = 10) -> None:
    """
    Print the most recent `limit` history entries to the console.

    Parameters
    ----------
    limit : int – Maximum number of entries to show (default 10)
    """
    history = load_history()

    if not history:
        print("\n  ℹ️   No search history found. Start searching to build history!\n")
        return

    recent = history[-limit:][::-1]          # Reverse to show newest first

    _print_section_header(f"📋  RECENT SEARCHES  (last {len(recent)} of {len(history)} total)")

    for entry in recent:
        rain_tag = " 🌧️ Rain" if entry.get("rain_1h", 0) > 0 else ""
        print(
            f"  [{entry.get('search_id', '?'):>3}]  "
            f"{entry.get('searched_at', 'N/A'):<20}  "
            f"{entry.get('city', 'Unknown'):<18} {entry.get('country', ''):<3}  "
            f"{entry.get('temperature', '?'):>5}°C  "
            f"{entry.get('condition', ''):.<16}  "
            f"Humidity: {entry.get('humidity', '?')}%"
            f"{rain_tag}"
        )

    print()



def filter_by_temperature(min_temp: float) -> list:
    """
    Return history entries where temperature >= min_temp.

    Parameters
    ----------
    min_temp : float – Minimum temperature threshold (°C)

    Returns
    -------
    list – Filtered history records
    """
    history = load_history()
    filtered = [
        entry for entry in history
        if entry.get("temperature", float("-inf")) >= min_temp
    ]
    logger.info(f"Temperature filter (>= {min_temp}°C) returned {len(filtered)} results.")
    return filtered


def filter_by_rain() -> list:
    """
    Return history entries where rain was recorded (rain_1h > 0).

    Returns
    -------
    list – Filtered history records
    """
    history = load_history()
    filtered = [
        entry for entry in history
        if entry.get("rain_1h", 0) > 0
        or "rain" in entry.get("condition", "").lower()
    ]
    logger.info(f"Rain filter returned {len(filtered)} results.")
    return filtered


def filter_by_humidity(min_humidity: int) -> list:
    """
    Return history entries where humidity >= min_humidity.

    Parameters
    ----------
    min_humidity : int – Minimum humidity threshold (%)

    Returns
    -------
    list – Filtered history records
    """
    history = load_history()
    filtered = [
        entry for entry in history
        if entry.get("humidity", 0) >= min_humidity
    ]
    logger.info(f"Humidity filter (>= {min_humidity}%) returned {len(filtered)} results.")
    return filtered


def display_filtered_results(results: list, filter_label: str) -> None:
    """
    Pretty-print a list of filtered history entries.

    Parameters
    ----------
    results      : list – Filtered records
    filter_label : str  – Human-readable description of the applied filter
    """
    if not results:
        print(f"\n  ℹ️   No history entries match the filter: {filter_label}\n")
        return

    _print_section_header(f"🔍  FILTER RESULTS  –  {filter_label}  ({len(results)} found)")

    for entry in results:
        rain_tag = f"  🌧️  Rain: {entry.get('rain_1h', 0)} mm" if entry.get("rain_1h", 0) > 0 else ""
        print(
            f"  {entry.get('searched_at', 'N/A'):<20}  "
            f"{entry.get('city', 'Unknown'):<18} {entry.get('country', ''):<3}  "
            f"Temp: {entry.get('temperature', '?'):>5}°C  "
            f"Humidity: {entry.get('humidity', '?'):>3}%"
            f"{rain_tag}"
        )

    print()



def _write_history(history: list) -> None:
    """Persist the history list to disk, creating the directory if needed."""
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as fh:
        json.dump(history, fh, indent=2, ensure_ascii=False)


def _print_section_header(title: str) -> None:
    """Print a consistent bordered section header."""
    line = "─" * 74
    print(f"\n  {line}")
    print(f"  {title}")
    print(f"  {line}")