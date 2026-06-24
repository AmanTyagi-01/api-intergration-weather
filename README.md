# ⛅ Weather Intelligence Dashboard

> A professional, portfolio-grade Python CLI application for real-time weather analytics — built as an internship-level project showcasing API integration, modular architecture, data persistence, and clean console UX.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [API Key Setup](#api-key-setup)
- [Usage](#usage)
- [Sample Input / Output](#sample-input--output)
- [Module Reference](#module-reference)
- [Technical Details](#technical-details)
- [Future Enhancements](#future-enhancements)
- [Screenshots](#screenshots)
- [License](#license)

---

## Overview

**Weather Intelligence Dashboard** is a command-line weather analytics tool written in pure Python. It connects to the [OpenWeatherMap Current Weather API](https://openweathermap.org/api/one-call-3), parses JSON responses, and presents data in a structured, colour-coded dashboard — all while persisting search history, supporting multi-criteria filtering, and exporting results to CSV and JSON.

This project was built to demonstrate:

- Real-world **REST API integration** using the `requests` library
- Structured **JSON parsing** and data transformation
- **Modular architecture** with clear separation of concerns
- Robust **exception handling** at every layer
- Professional **logging** using Python's `logging` module
- Clean, **ANSI-coloured CLI** output
- File I/O with **CSV** and **JSON** export pipelines
- **PEP 8** compliant, well-documented code

---

## Features

| # | Feature | Description |
|---|---------|-------------|
| A | **Weather Search** | Search any city worldwide by name with input validation |
| B | **Full Weather Card** | Temperature, feels-like, min/max, humidity, pressure, wind, visibility, precipitation, sunrise/sunset |
| C | **Search History** | Persistent JSON history of all past searches (last 50 entries) |
| D | **Filtering System** | Filter history by min temperature, rain presence, or min humidity |
| E | **Export** | Export single results or full history to CSV and/or JSON |
| F | **Logging** | Structured log file at `logs/app.log` — captures all API calls, errors, and user actions |

---

## Project Structure

```
Weather_Intelligence_Dashboard/
│
├── main.py               ← Entry point, menu system, display logic, ANSI UI
├── weather_api.py        ← OpenWeatherMap API calls, JSON parsing, validation
├── history_manager.py    ← Search history CRUD, filtering, display
├── exporter.py           ← CSV & JSON export pipeline
│
├── logs/
│   └── app.log           ← Rotating application log (auto-created)
│
├── data/
│   ├── history.json      ← Persistent search history (auto-created)
│   ├── weather_export.csv    ← CSV export (grows with each export)
│   └── weather_export.json   ← JSON export array
│
├── screenshots/          ← Add your own screenshots here
├── requirements.txt      ← Python dependencies
└── README.md             ← This file
```

---

## Installation

### Prerequisites

- Python **3.10 or higher**
- `pip` package manager
- An [OpenWeatherMap](https://openweathermap.org/) free account

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/yourusername/Weather_Intelligence_Dashboard.git
cd Weather_Intelligence_Dashboard

# 2. (Optional but recommended) Create a virtual environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API key (see next section)

# 5. Run the application
python main.py
```

---

## API Key Setup

### Step 1 – Register
Go to [https://openweathermap.org/api](https://openweathermap.org/api) and create a **free account**.

### Step 2 – Get Your Key
After logging in, navigate to:
> **API keys** → Copy the default key (or generate a new one)

> ⚠️ **Note:** New API keys may take up to **2 hours** to activate after registration.

### Step 3 – Configure the Key

**Option A – Environment Variable (Recommended)**

```bash
# Windows (Command Prompt)
set OWM_API_KEY=your_api_key_here

# Windows (PowerShell)
$env:OWM_API_KEY="your_api_key_here"

# macOS / Linux
export OWM_API_KEY=your_api_key_here
```

**Option B – Edit main.py Directly**

Open `main.py` and replace the placeholder on line ~35:

```python
API_KEY = "your_api_key_here"   # ← paste your key here
```

> 🔒 If pushing to GitHub, **use Option A** (environment variable) and add `main.py` to `.gitignore`, or use a `.env` file with `python-dotenv`.

---

## Usage

```bash
python main.py
```

### Main Menu

```
  ┌─────────────────────────────────────────────────┐
  │              MAIN MENU                          │
  ├─────────────────────────────────────────────────┤
  │  1  🔍  Search Weather by City                  │
  │  2  📋  View Search History                     │
  │  3  🔽  Filter History                          │
  │  4  📁  Export Summary                          │
  │  5  🗑️   Clear Search History                   │
  │  6  ℹ️   About / Help                           │
  │  0  🚪  Exit                                    │
  └─────────────────────────────────────────────────┘
```

### Filter Sub-Menu

```
  ┌─────────────────────────────────────────────────┐
  │              FILTER OPTIONS                     │
  ├─────────────────────────────────────────────────┤
  │  1  🌡️   Filter by Minimum Temperature          │
  │  2  🌧️   Filter Cities with Rain                │
  │  3  💧  Filter by Minimum Humidity              │
  │  0  ◀   Back to Main Menu                       │
  └─────────────────────────────────────────────────┘
```

---

## Sample Input / Output

### City Search

**Input:**
```
  City ▶  London
```

**Output:**
```
  ──────────────────────────────────────────────────────────────────────────
  🌍  WEATHER REPORT  –  London, GB             Fetched: 2024-06-20 14:32:01
  ──────────────────────────────────────────────────────────────────────────

  ⛅  Overcast Clouds   (Cloud cover: 100%)

  🌡️  TEMPERATURE
  ────────────────────────────────────────
  Current ................  18.4 °C
  Feels Like .............  17.9 °C
  Min / Max ..............  16.2 °C  /  20.1 °C

  💧  ATMOSPHERE
  ────────────────────────────────────────
  Humidity ...............  72 %
  Pressure ...............  1013 hPa
  Visibility .............  10.0 km

  💨  WIND
  ────────────────────────────────────────
  Speed ..................  3.6 m/s  (SW)
  Gust ...................  5.1 m/s

  ☀️  SUN
  ────────────────────────────────────────
  Sunrise ................  04:43 AM
  Sunset .................  09:21 PM

  📍  LOCATION
  ────────────────────────────────────────
  Coordinates ............  Lat 51.5085  /  Lon -0.1257
  ──────────────────────────────────────────────────────────────────────────
```

### Invalid City

**Input:**
```
  City ▶  xyzabc123
```

**Output:**
```
  ⚠️   City name should not contain numbers. Please try again.
```

### Temperature Filter

**Input:**
```
  Enter minimum temperature (°C) ▶  25
```

**Output:**
```
  ──────────────────────────────────────────────────────────────────────────
  🔍  FILTER RESULTS  –  Temperature ≥ 25°C  (3 found)
  ──────────────────────────────────────────────────────────────────────────
  2024-06-20 10:11:05   Dubai              AE   40.2°C  Humidity:  35%
  2024-06-20 11:23:44   Mumbai             IN   32.1°C  Humidity:  80%  🌧️ Rain
  2024-06-20 13:05:17   Cairo              EG   27.8°C  Humidity:  41%
```

### Export Prompt

After every successful weather fetch:
```
  Export this result?  [C]SV   [J]SON   [B]oth   [Enter] Skip
  ▶  B

  ✅  Data exported to CSV  →  data/weather_export.csv
  ✅  Data exported to JSON →  data/weather_export.json
```

---

## Module Reference

### `main.py`
The application entry point. Responsibilities:
- Logging setup (file + console handlers)
- API key validation and configuration
- ANSI colour constants and UI helpers
- Full interactive menu loop
- Weather card rendering (`display_weather`)
- Export prompt after each search

### `weather_api.py`
All API interaction. Responsibilities:
- `fetch_weather(city, api_key)` – main public function
- `_validate_city_input()` – guards against empty / numeric input
- `_parse_weather()` – transforms raw JSON into a clean flat dict
- `_utc_to_local_time()` – converts UNIX timestamps to readable local time
- `_degrees_to_compass()` – converts wind degrees to 16-point compass
- HTTP error mapping (401, 404, 429, 500, 503)

### `history_manager.py`
Persistent search history. Responsibilities:
- `save_to_history()` / `load_history()` / `clear_history()`
- `display_history(limit)` – tabular history display
- `filter_by_temperature()`, `filter_by_rain()`, `filter_by_humidity()`
- `display_filtered_results()` – renders filter output

### `exporter.py`
Data export pipeline. Responsibilities:
- `export_to_csv()` – appends to `data/weather_export.csv`
- `export_to_json()` – appends to JSON array in `data/weather_export.json`
- `export_history_to_csv()` – dumps full history to `data/history_export.csv`
- `display_export_summary()` – shows file size and record counts

---

## Technical Details

| Item | Detail |
|------|--------|
| API | OpenWeatherMap Current Weather API v2.5 |
| HTTP Client | `requests` 2.31 |
| Data Format | JSON (API) → dict → CSV / JSON (export) |
| Units | Metric (°C, m/s, mm) — configurable in `weather_api.py` |
| History Cap | 50 most recent searches |
| Timeout | 10 seconds per API request |
| Logging | `logging.DEBUG` to file, `logging.WARNING` to console |
| Encoding | UTF-8 throughout |
| Python | 3.10+ (uses `dict | None` union type hint) |

### Error Handling Strategy

Every layer has its own try/except coverage:

```
User Input → _validate_city_input()
               ↓
API Call  → requests.get() wrapped in:
             ConnectionError, Timeout, HTTPError, RequestException
               ↓
JSON Parse → _parse_weather() with .get() defaults
               ↓
File I/O  → OSError, PermissionError, json.JSONDecodeError
               ↓
Main Loop → catch-all Exception with logging + graceful recovery
```

---

## Future Enhancements

| Priority | Feature |
|----------|---------|
| 🔴 High | **5-Day Forecast** – Use the `/forecast` endpoint for a 5-day, 3-hour forecast grid |
| 🔴 High | **dotenv support** – Use `python-dotenv` to load API key from `.env` file |
| 🟡 Medium | **Multi-city comparison** – Fetch and compare weather for 2–5 cities side-by-side |
| 🟡 Medium | **Unit toggle** – Runtime switch between Metric and Imperial without restarting |
| 🟡 Medium | **Air Quality Index** – Integrate OWM Air Pollution API |
| 🟢 Low | **Rich / Textual TUI** – Upgrade CLI with `rich` library for tables and colour |
| 🟢 Low | **Flask Web UI** – Wrap the backend in a Flask REST API with a simple HTML frontend |
| 🟢 Low | **Scheduled alerts** – Cron/scheduler to push weather alerts via email or Telegram |
| 🟢 Low | **SQLite backend** – Replace JSON history with a proper SQLite database |
| 🟢 Low | **Unit tests** – `pytest` test suite with mocked API responses |

---

## Screenshots

> 📸 Add your own screenshots to the `screenshots/` directory and reference them here.

```
screenshots/
├── 01_main_menu.png
├── 02_weather_card_london.png
├── 03_search_history.png
├── 04_filter_results.png
└── 05_export_summary.png
```

---

## License

This project is released for educational and portfolio purposes.  
OpenWeatherMap API data is subject to their [Terms of Service](https://openweathermap.org/terms).

---

*Built with ❤️ using Python · Powered by OpenWeatherMap*
