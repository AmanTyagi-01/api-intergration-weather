"""
exporter.py
===========
Handles exporting weather data and search history to CSV and JSON formats.
All exports are saved to the data/ directory.

Author  : Weather Intelligence Dashboard
Version : 1.0.0
"""

import csv
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

DATA_DIR        = "data"
CSV_FILE        = os.path.join(DATA_DIR, "weather_export.csv")
JSON_FILE       = os.path.join(DATA_DIR, "weather_export.json")

CSV_FIELDNAMES = [
    "exported_at",
    "city",
    "country",
    "latitude",
    "longitude",
    "temperature",
    "feels_like",
    "temp_min",
    "temp_max",
    "humidity",
    "pressure",
    "visibility_km",
    "wind_speed",
    "wind_direction",
    "wind_gust",
    "rain_1h",
    "snow_1h",
    "condition",
    "description",
    "cloud_cover",
    "sunrise",
    "sunset",
    "fetched_at",
]



def export_to_csv(weather_data: dict) -> bool:
    """
    Append a weather record to the CSV export file.
    Creates the file with a header row if it does not yet exist.

    Parameters
    ----------
    weather_data : dict – Parsed weather dictionary from weather_api.py

    Returns
    -------
    bool – True on success, False on failure
    """
    try:
        _ensure_data_dir()
        file_exists = os.path.isfile(CSV_FILE) and os.path.getsize(CSV_FILE) > 0

        with open(CSV_FILE, "a", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=CSV_FIELDNAMES,
                                    extrasaction="ignore")

            if not file_exists:
                writer.writeheader()
                logger.info("Created new CSV export file with header row.")

            row = _build_csv_row(weather_data)
            writer.writerow(row)

        city = weather_data.get("city", "Unknown")
        logger.info(f"Exported '{city}' data to CSV: {CSV_FILE}")
        print(f"\n  ✅  Data exported to CSV  →  {CSV_FILE}\n")
        return True

    except PermissionError:
        logger.error(f"Permission denied writing to {CSV_FILE}.")
        print(f"\n  ❌  Permission denied: cannot write to {CSV_FILE}\n")
        return False

    except OSError as err:
        logger.exception(f"OS error during CSV export: {err}")
        print(f"\n  ❌  Export failed: {err}\n")
        return False


def export_to_json(weather_data: dict) -> bool:
    """
    Append a weather record to the JSON export file.
    The file stores a JSON array of all exported entries.

    Parameters
    ----------
    weather_data : dict – Parsed weather dictionary from weather_api.py

    Returns
    -------
    bool – True on success, False on failure
    """
    try:
        _ensure_data_dir()

        existing = _load_json_export()

        entry = dict(weather_data)                    # Shallow copy
        entry["exported_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        existing.append(entry)

        with open(JSON_FILE, "w", encoding="utf-8") as fh:
            json.dump(existing, fh, indent=2, ensure_ascii=False)

        city = weather_data.get("city", "Unknown")
        logger.info(f"Exported '{city}' data to JSON: {JSON_FILE}")
        print(f"  ✅  Data exported to JSON  →  {JSON_FILE}\n")
        return True

    except OSError as err:
        logger.exception(f"OS error during JSON export: {err}")
        print(f"\n  ❌  JSON export failed: {err}\n")
        return False


def export_history_to_csv(history: list) -> bool:
    """
    Export the entire search history list to a separate CSV file.

    Parameters
    ----------
    history : list – List of history dictionaries from history_manager

    Returns
    -------
    bool – True on success, False on failure
    """
    if not history:
        print("\n  ℹ️   No history data to export.\n")
        return False

    _ensure_data_dir()
    history_csv = os.path.join(DATA_DIR, "history_export.csv")

    fieldnames = list(history[0].keys())

    try:
        with open(history_csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames,
                                    extrasaction="ignore")
            writer.writeheader()
            writer.writerows(history)

        logger.info(f"Exported {len(history)} history records to {history_csv}")
        print(f"\n  ✅  History exported to CSV  →  {history_csv}\n")
        return True

    except OSError as err:
        logger.exception(f"Failed to export history CSV: {err}")
        print(f"\n  ❌  History CSV export failed: {err}\n")
        return False


def display_export_summary() -> None:
    """
    Print a summary of the current export files (path, size, record count).
    """
    print("\n  📁  EXPORT FILE SUMMARY")
    print("  " + "─" * 60)

    _summarize_file("CSV Export",  CSV_FILE,  _count_csv_rows)
    _summarize_file("JSON Export", JSON_FILE, _count_json_entries)

    print()



def _build_csv_row(weather_data: dict) -> dict:
    """Add the export timestamp and return a CSV-ready row dict."""
    row = {field: weather_data.get(field, "") for field in CSV_FIELDNAMES}
    row["exported_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return row


def _load_json_export() -> list:
    """Load the JSON export array from disk, or return [] if absent/corrupt."""
    if not os.path.isfile(JSON_FILE):
        return []
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def _ensure_data_dir() -> None:
    """Create the data/ directory if it does not exist."""
    os.makedirs(DATA_DIR, exist_ok=True)


def _summarize_file(label: str, path: str,
                    count_fn) -> None:
    """Print one line of the export summary for a given file."""
    if os.path.isfile(path):
        size_kb = os.path.getsize(path) / 1024
        count   = count_fn(path)
        print(f"  {label:<15}  {path:<40}  "
              f"{size_kb:>6.1f} KB   {count} record(s)")
    else:
        print(f"  {label:<15}  {path:<40}  (file not created yet)")


def _count_csv_rows(path: str) -> int:
    """Return the number of data rows in a CSV (excludes header)."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            reader = csv.reader(fh)
            rows = sum(1 for _ in reader)
        return max(rows - 1, 0)    # Subtract header
    except OSError:
        return 0


def _count_json_entries(path: str) -> int:
    """Return the number of entries in the JSON export array."""
    data = _load_json_export()
    return len(data)