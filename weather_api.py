"""
weather_api.py
==============
Handles all interactions with the OpenWeatherMap API.
Responsible for fetching, validating, and parsing weather data.

Author  : Weather Intelligence Dashboard
Version : 1.0.0
"""

import requests
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
UNITS = "metric"          # "metric" → °C | "imperial" → °F
TIMEOUT_SECONDS = 10      # Max seconds to wait for API response



def fetch_weather(city: str, api_key: str) -> dict | None:
    """
    Fetch current weather data for a given city from OpenWeatherMap.

    Parameters
    ----------
    city    : str  – City name (e.g. "London", "New Delhi")
    api_key : str  – Valid OpenWeatherMap API key

    Returns
    -------
    dict | None
        Parsed weather dictionary on success, None on failure.
    """
    if not _validate_city_input(city):
        return None

    params = {
        "q":       city.strip(),
        "appid":   api_key,
        "units":   UNITS,
    }

    try:
        logger.info(f"Requesting weather data for city: '{city}'")
        response = requests.get(BASE_URL, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()                   # Raises HTTPError for 4xx/5xx

        raw_json = response.json()
        weather_data = _parse_weather(raw_json)

        logger.info(f"Successfully fetched weather for '{city}' "
                    f"(status code: {response.status_code})")
        return weather_data

    except requests.exceptions.ConnectionError:
        logger.error("Connection error – check your internet connection.")
        print("\n  ❌  No internet connection. Please check your network.\n")

    except requests.exceptions.Timeout:
        logger.error(f"Request timed out after {TIMEOUT_SECONDS}s for city '{city}'.")
        print(f"\n  ❌  Request timed out ({TIMEOUT_SECONDS}s). Try again later.\n")

    except requests.exceptions.HTTPError as http_err:
        status = http_err.response.status_code
        _handle_http_error(status, city)

    except requests.exceptions.RequestException as req_err:
        logger.exception(f"Unexpected request error for '{city}': {req_err}")
        print(f"\n  ❌  Unexpected error: {req_err}\n")

    return None



def _validate_city_input(city: str) -> bool:
    """
    Validate that the city name is a non-empty string with no digits.

    Returns True if valid, prints an error and returns False otherwise.
    """
    if not city or not city.strip():
        logger.warning("Empty city name submitted.")
        print("\n  ⚠️   City name cannot be empty. Please try again.\n")
        return False

    if any(char.isdigit() for char in city):
        logger.warning(f"Invalid city name with digits submitted: '{city}'")
        print("\n  ⚠️   City name should not contain numbers. Please try again.\n")
        return False

    if len(city.strip()) < 2:
        logger.warning(f"City name too short: '{city}'")
        print("\n  ⚠️   City name must be at least 2 characters long.\n")
        return False

    return True


def _handle_http_error(status_code: int, city: str) -> None:
    """Map common HTTP status codes to user-friendly messages."""
    messages = {
        401: "❌  Invalid API key. Please check your OpenWeatherMap API key.",
        404: f"❌  City '{city}' not found. Check the spelling and try again.",
        429: "❌  API rate limit exceeded. Please wait a moment before retrying.",
        500: "❌  OpenWeatherMap server error. Try again later.",
        503: "❌  OpenWeatherMap service is temporarily unavailable.",
    }
    message = messages.get(status_code,
                           f"❌  HTTP error {status_code} received from API.")
    logger.error(f"HTTP {status_code} for city '{city}': {message}")
    print(f"\n  {message}\n")


def _parse_weather(data: dict) -> dict:
    """
    Parse raw OpenWeatherMap JSON into a clean, flat dictionary.

    Parameters
    ----------
    data : dict – Raw JSON response from the API

    Returns
    -------
    dict – Structured weather data ready for display / export
    """
    timezone_offset = data.get("timezone", 0)          # UTC offset in seconds
    sunrise_utc  = data["sys"]["sunrise"]
    sunset_utc   = data["sys"]["sunset"]

    sunrise_local = _utc_to_local_time(sunrise_utc, timezone_offset)
    sunset_local  = _utc_to_local_time(sunset_utc,  timezone_offset)

    visibility_m  = data.get("visibility", 0)
    visibility_km = round(visibility_m / 1000, 2)

    wind_deg = data.get("wind", {}).get("deg", 0)
    wind_direction = _degrees_to_compass(wind_deg)

    rain_1h  = data.get("rain",  {}).get("1h", 0.0)
    snow_1h  = data.get("snow",  {}).get("1h", 0.0)

    return {
        "city":            data["name"],
        "country":         data["sys"]["country"],
        "latitude":        data["coord"]["lat"],
        "longitude":       data["coord"]["lon"],
        "timezone_offset": timezone_offset,

        "temperature":     round(data["main"]["temp"],       1),
        "feels_like":      round(data["main"]["feels_like"], 1),
        "temp_min":        round(data["main"]["temp_min"],   1),
        "temp_max":        round(data["main"]["temp_max"],   1),

        "humidity":        data["main"]["humidity"],         # %
        "pressure":        data["main"]["pressure"],         # hPa
        "visibility_km":   visibility_km,

        "wind_speed":      data["wind"].get("speed", 0),     # m/s
        "wind_direction":  wind_direction,
        "wind_gust":       data.get("wind", {}).get("gust", 0),

        "rain_1h":         rain_1h,                          # mm
        "snow_1h":         snow_1h,                          # mm

        "condition":       data["weather"][0]["main"],
        "description":     data["weather"][0]["description"].title(),
        "cloud_cover":     data["clouds"]["all"],            # %

        "sunrise":         sunrise_local,
        "sunset":          sunset_local,

        "fetched_at":      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _utc_to_local_time(utc_timestamp: int, offset_seconds: int) -> str:
    """
    Convert a UTC UNIX timestamp to a human-readable local time string.

    Parameters
    ----------
    utc_timestamp  : int – UNIX timestamp (seconds since epoch)
    offset_seconds : int – UTC offset in seconds

    Returns
    -------
    str – Formatted time, e.g. "06:32 AM"
    """
    try:
        utc_dt    = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
        local_ts  = utc_timestamp + offset_seconds
        local_dt  = datetime.fromtimestamp(local_ts, tz=timezone.utc)
        return local_dt.strftime("%I:%M %p")
    except (OSError, OverflowError, ValueError) as e:
        logger.warning(f"Could not convert timestamp {utc_timestamp}: {e}")
        return "N/A"


def _degrees_to_compass(degrees: int) -> str:
    """Convert wind direction from degrees to 16-point compass rose."""
    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]