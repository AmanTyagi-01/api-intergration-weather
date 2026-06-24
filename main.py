"""
main.py
=======
Weather Intelligence Dashboard – Entry Point
============================================
A professional CLI weather analytics tool that fetches real-time weather data
from OpenWeatherMap, maintains a searchable history, supports filtering, and
exports results to CSV / JSON.

Usage
-----
    python main.py

Requirements
------------
    pip install requests

    Set your OpenWeatherMap API key in the API_KEY constant below,
    or export it as an environment variable:
        Windows : set OWM_API_KEY=your_key_here
        macOS/Linux : export OWM_API_KEY=your_key_here

Author  : Weather Intelligence Dashboard
Version : 1.0.0
"""

import logging
import os
import sys

import weather_api
import history_manager
import exporter


API_KEY = os.environ.get("OWM_API_KEY", "")

LOG_DIR  = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logging() -> None:
    """
    Configure root logger to write to both a rotating log file and the console.
    Console output is restricted to WARNING+ to keep the UI clean.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)        # Capture everything at root level

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        fmt="%(asctime)s  [%(levelname)-8s]  %(name)s  –  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_fmt)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_fmt = logging.Formatter(fmt="  ⚠  %(message)s")
    console_handler.setFormatter(console_fmt)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


logger = logging.getLogger(__name__)


_USE_COLOUR = sys.platform != "win32" or os.environ.get("TERM") == "xterm"

RESET  = "\033[0m"  if _USE_COLOUR else ""
BOLD   = "\033[1m"  if _USE_COLOUR else ""
CYAN   = "\033[96m" if _USE_COLOUR else ""
GREEN  = "\033[92m" if _USE_COLOUR else ""
YELLOW = "\033[93m" if _USE_COLOUR else ""
BLUE   = "\033[94m" if _USE_COLOUR else ""
RED    = "\033[91m" if _USE_COLOUR else ""
DIM    = "\033[2m"  if _USE_COLOUR else ""


def clear_screen() -> None:
    """Clear the terminal screen cross-platform."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner() -> None:
    """Print the application banner / title card."""
    banner = f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║        ⛅  WEATHER INTELLIGENCE DASHBOARD  v1.0.0                       ║
║                                                                          ║
║        Real-Time Weather Analytics  |  Powered by OpenWeatherMap         ║
║                                                                          ║
╚══════════════════════════════════════════════════════════════════════════╝
{RESET}"""
    print(banner)


def print_main_menu() -> None:
    """Print the interactive main menu."""
    print(f"{BOLD}  ┌─────────────────────────────────────────────────┐{RESET}")
    print(f"{BOLD}  │              MAIN MENU                          │{RESET}")
    print(f"{BOLD}  ├─────────────────────────────────────────────────┤{RESET}")
    print(f"  │  {GREEN}1{RESET}  🔍  Search Weather by City                   │")
    print(f"  │  {GREEN}2{RESET}  📋  View Search History                       │")
    print(f"  │  {GREEN}3{RESET}  🔽  Filter History                            │")
    print(f"  │  {GREEN}4{RESET}  📁  Export Summary                            │")
    print(f"  │  {GREEN}5{RESET}  🗑️   Clear Search History                    │")
    print(f"  │  {GREEN}6{RESET}  ℹ️   About / Help                            │")
    print(f"  │  {GREEN}0{RESET}  🚪  Exit                                      │")
    print(f"{BOLD}  └─────────────────────────────────────────────────┘{RESET}")
    print()


def print_filter_menu() -> None:
    """Print the filter sub-menu."""
    print(f"\n{BOLD}  ┌─────────────────────────────────────────────────┐{RESET}")
    print(f"{BOLD}  │              FILTER OPTIONS                      │{RESET}")
    print(f"{BOLD}  ├─────────────────────────────────────────────────┤{RESET}")
    print(f"  │  {YELLOW}1{RESET}  🌡️   Filter by Minimum Temperature           │")
    print(f"  │  {YELLOW}2{RESET}  🌧️   Filter Cities with Rain                  │")
    print(f"  │  {YELLOW}3{RESET}  💧  Filter by Minimum Humidity               │")
    print(f"  │  {YELLOW}0{RESET}  ◀   Back to Main Menu                        │")
    print(f"{BOLD}  └─────────────────────────────────────────────────┘{RESET}")
    print()


def display_weather(data: dict) -> None:
    """
    Render a comprehensive, well-formatted weather card to the console.

    Parameters
    ----------
    data : dict – Parsed weather dictionary from weather_api.py
    """
    city    = data.get("city", "N/A")
    country = data.get("country", "N/A")
    fetched = data.get("fetched_at", "N/A")

    condition_emoji = _condition_to_emoji(data.get("condition", ""))

    sep = "─" * 74

    print(f"\n{CYAN}{BOLD}  {sep}{RESET}")
    print(f"{CYAN}{BOLD}  🌍  WEATHER REPORT  –  {city}, {country}            "
          f"  Fetched: {fetched}{RESET}")
    print(f"{CYAN}{BOLD}  {sep}{RESET}")

    print(f"\n  {condition_emoji}  {BOLD}{data.get('description', 'N/A')}{RESET}"
          f"   (Cloud cover: {data.get('cloud_cover', 0)}%)")

    _print_row_header("🌡️  TEMPERATURE")
    print(f"  {'Current':.<25}  {GREEN}{BOLD}{data.get('temperature', 'N/A')} °C{RESET}")
    print(f"  {'Feels Like':.<25}  {data.get('feels_like', 'N/A')} °C")
    print(f"  {'Min / Max':.<25}  {data.get('temp_min', 'N/A')} °C  /  "
          f"{data.get('temp_max', 'N/A')} °C")

    _print_row_header("💧  ATMOSPHERE")
    print(f"  {'Humidity':.<25}  {data.get('humidity', 'N/A')} %")
    print(f"  {'Pressure':.<25}  {data.get('pressure', 'N/A')} hPa")
    print(f"  {'Visibility':.<25}  {data.get('visibility_km', 'N/A')} km")

    _print_row_header("💨  WIND")
    print(f"  {'Speed':.<25}  {data.get('wind_speed', 'N/A')} m/s  "
          f"({data.get('wind_direction', 'N/A')})")
    gust = data.get("wind_gust", 0)
    if gust:
        print(f"  {'Gust':.<25}  {gust} m/s")

    rain = data.get("rain_1h", 0)
    snow = data.get("snow_1h", 0)
    if rain or snow:
        _print_row_header("🌧️  PRECIPITATION (last 1 hour)")
        if rain:
            print(f"  {'Rainfall':.<25}  {rain} mm")
        if snow:
            print(f"  {'Snowfall':.<25}  {snow} mm")

    _print_row_header("☀️  SUN")
    print(f"  {'Sunrise':.<25}  {data.get('sunrise', 'N/A')}")
    print(f"  {'Sunset':.<25}  {data.get('sunset', 'N/A')}")

    _print_row_header("📍  LOCATION")
    print(f"  {'Coordinates':.<25}  "
          f"Lat {data.get('latitude', 'N/A')}  /  "
          f"Lon {data.get('longitude', 'N/A')}")

    print(f"\n{CYAN}  {sep}{RESET}\n")

    _offer_export(data)


def _print_row_header(label: str) -> None:
    """Print a coloured section label inside the weather card."""
    print(f"\n  {YELLOW}{BOLD}{label}{RESET}")
    print(f"  {'─' * 40}")


def _offer_export(data: dict) -> None:
    """Ask the user if they want to export the current result."""
    print(f"  {DIM}Export this result?  "
          f"[{GREEN}C{RESET}{DIM}]SV   [{GREEN}J{RESET}{DIM}]SON   "
          f"[{GREEN}B{RESET}{DIM}]oth   [Enter] Skip{RESET}")

    choice = input("  ▶  ").strip().upper()

    if choice in ("C", "B"):
        exporter.export_to_csv(data)
    if choice in ("J", "B"):
        exporter.export_to_json(data)


def _condition_to_emoji(condition: str) -> str:
    """Return a suitable emoji for a given OpenWeatherMap condition string."""
    mapping = {
        "Thunderstorm": "⛈️",
        "Drizzle":      "🌦️",
        "Rain":         "🌧️",
        "Snow":         "❄️",
        "Mist":         "🌫️",
        "Fog":          "🌫️",
        "Haze":         "🌫️",
        "Smoke":        "🌫️",
        "Dust":         "🌪️",
        "Sand":         "🌪️",
        "Ash":          "🌋",
        "Squall":       "🌬️",
        "Tornado":      "🌪️",
        "Clear":        "☀️",
        "Clouds":       "☁️",
    }
    return mapping.get(condition, "🌡️")



def handle_weather_search() -> None:
    """Prompt for a city name, fetch weather, display and save to history."""
    print(f"\n{BOLD}  🔍  CITY WEATHER SEARCH{RESET}")
    print("  " + "─" * 40)
    print("  Enter a city name (or 'back' to return to menu)")

    city = input("  City ▶  ").strip()

    if city.lower() in ("back", "b", ""):
        return

    logger.info(f"User initiated search for city: '{city}'")
    print(f"\n  ⏳  Fetching weather for '{city}' …\n")

    data = weather_api.fetch_weather(city, API_KEY)

    if data:
        display_weather(data)
        saved = history_manager.save_to_history(data)
        if saved:
            print(f"  {DIM}✓ Search saved to history.{RESET}\n")
    else:
        print(f"  {RED}No data returned for '{city}'. Please try another city.{RESET}\n")
        logger.warning(f"Search returned no data for city: '{city}'")


def handle_view_history() -> None:
    """Show recent searches and optionally export full history."""
    print(f"\n{BOLD}  📋  SEARCH HISTORY{RESET}")
    try:
        limit_str = input("  How many recent entries to display? [10] ▶  ").strip()
        limit = int(limit_str) if limit_str.isdigit() else 10
        limit = max(1, min(limit, 50))            # Clamp between 1 and 50
    except ValueError:
        limit = 10

    history_manager.display_history(limit=limit)

    print(f"  {DIM}Export full history to CSV?  [Y/N]{RESET}")
    if input("  ▶  ").strip().upper() == "Y":
        full_history = history_manager.load_history()
        exporter.export_history_to_csv(full_history)


def handle_filter_menu() -> None:
    """Render the filter sub-menu and execute chosen filter."""
    while True:
        print_filter_menu()
        choice = input("  Select filter ▶  ").strip()

        if choice == "1":
            _filter_by_temperature()
        elif choice == "2":
            _filter_by_rain()
        elif choice == "3":
            _filter_by_humidity()
        elif choice == "0":
            break
        else:
            print(f"\n  {RED}Invalid option. Please choose 0–3.{RESET}\n")


def _filter_by_temperature() -> None:
    """Execute temperature filter."""
    print(f"\n  {BOLD}Minimum Temperature Filter{RESET}")
    try:
        raw = input("  Enter minimum temperature (°C) ▶  ").strip()
        min_temp = float(raw)
    except ValueError:
        print(f"\n  {RED}Invalid input. Please enter a numeric temperature.{RESET}\n")
        return

    results = history_manager.filter_by_temperature(min_temp)
    history_manager.display_filtered_results(
        results, f"Temperature ≥ {min_temp}°C"
    )


def _filter_by_rain() -> None:
    """Execute rain filter."""
    results = history_manager.filter_by_rain()
    history_manager.display_filtered_results(results, "Cities with Rain")


def _filter_by_humidity() -> None:
    """Execute humidity filter."""
    print(f"\n  {BOLD}Minimum Humidity Filter{RESET}")
    try:
        raw = input("  Enter minimum humidity (%) ▶  ").strip()
        min_hum = int(raw)
        if not 0 <= min_hum <= 100:
            raise ValueError("Out of range")
    except ValueError:
        print(f"\n  {RED}Invalid input. Enter a number between 0 and 100.{RESET}\n")
        return

    results = history_manager.filter_by_humidity(min_hum)
    history_manager.display_filtered_results(
        results, f"Humidity ≥ {min_hum}%"
    )


def handle_export_summary() -> None:
    """Display export file summary."""
    exporter.display_export_summary()


def handle_clear_history() -> None:
    """Confirm and clear search history."""
    print(f"\n  {RED}{BOLD}⚠️  This will permanently delete all search history.{RESET}")
    confirm = input("  Type 'YES' to confirm ▶  ").strip()

    if confirm == "YES":
        history_manager.clear_history()
    else:
        print("  Cancelled – history was not cleared.\n")


def handle_about() -> None:
    """Display help and about information."""
    print(f"""
{CYAN}{BOLD}  ══════════════════════════════════════════════════════{RESET}
{BOLD}  ABOUT  –  Weather Intelligence Dashboard v1.0.0{RESET}
{CYAN}  ══════════════════════════════════════════════════════{RESET}

  A professional CLI weather analytics application powered
  by the OpenWeatherMap Current Weather API.

{BOLD}  FEATURES{RESET}
  • Real-time weather lookup for any city worldwide
  • Full weather card: temperature, humidity, wind,
    visibility, pressure, sunrise/sunset, precipitation
  • Search history with local JSON persistence
  • Powerful filtering: temperature, rain, humidity
  • Export results to CSV and JSON
  • Structured logging to logs/app.log

{BOLD}  DATA FILES{RESET}
  • data/history.json    – Search history
  • data/weather_export.csv  – CSV export
  • data/weather_export.json – JSON export
  • logs/app.log         – Application logs

{BOLD}  API KEY SETUP{RESET}
  1. Register free at https://openweathermap.org/api
  2. Copy your API key from the dashboard
  3. Set it in main.py (API_KEY = "...") OR
     export OWM_API_KEY=your_key_here

{BOLD}  TEMPERATURE UNITS{RESET}
  Currently set to Metric (°C / m/s).
  Change UNITS in weather_api.py to "imperial" for °F / mph.

{CYAN}  ══════════════════════════════════════════════════════{RESET}
""")
    input("  Press Enter to return to the menu…")



def validate_api_key(key: str) -> bool:
    """
    Basic structural validation of the API key before making any requests.

    Parameters
    ----------
    key : str – The API key string

    Returns
    -------
    bool – True if the key looks valid, False otherwise
    """
    if not key or key == "YOUR_OPENWEATHERMAP_API_KEY_HERE":
        return False
    if len(key) < 20:
        return False
    return True



def main() -> None:
    """Application entry point – runs the main interactive loop."""
    setup_logging()
    logger.info("Weather Intelligence Dashboard started.")

    clear_screen()
    print_banner()

    if not validate_api_key(API_KEY):
        print(f"\n{RED}{BOLD}  ❌  API KEY NOT CONFIGURED{RESET}\n")
        print("  Please set your OpenWeatherMap API key:")
        print("  Option 1: Edit main.py  →  API_KEY = 'your_key_here'")
        print("  Option 2: Set environment variable OWM_API_KEY=your_key_here\n")
        print("  Get a free key at: https://openweathermap.org/api\n")
        logger.critical("Application started without a valid API key.")
        sys.exit(1)

    logger.info("API key validation passed.")
    print(f"  {GREEN}✅  API key loaded.{RESET}  Ready to fetch weather data.\n")

    while True:
        try:
            print_main_menu()
            choice = input("  Select option ▶  ").strip()

            if choice == "1":
                handle_weather_search()

            elif choice == "2":
                handle_view_history()

            elif choice == "3":
                handle_filter_menu()

            elif choice == "4":
                handle_export_summary()

            elif choice == "5":
                handle_clear_history()

            elif choice == "6":
                handle_about()

            elif choice == "0":
                print(f"\n  {CYAN}👋  Thank you for using Weather Intelligence Dashboard.{RESET}")
                print(f"  {DIM}Goodbye!{RESET}\n")
                logger.info("Weather Intelligence Dashboard exited by user.")
                sys.exit(0)

            else:
                print(f"\n  {RED}Invalid option '{choice}'. Please choose 0–6.{RESET}\n")

        except KeyboardInterrupt:
            print(f"\n\n  {YELLOW}Ctrl+C detected. Exiting gracefully …{RESET}\n")
            logger.info("Application interrupted by user (Ctrl+C).")
            sys.exit(0)

        except Exception as exc:
            logger.exception(f"Unexpected error in main loop: {exc}")
            print(f"\n  {RED}An unexpected error occurred: {exc}{RESET}")
            print("  The error has been logged. Press Enter to continue.\n")
            input()


if __name__ == "__main__":
    main()