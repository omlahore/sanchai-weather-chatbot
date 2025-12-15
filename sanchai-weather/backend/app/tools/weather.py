import httpx
from typing import Optional

from langchain_core.tools import tool


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@tool("get_weather", args_schema=None)
async def get_weather(city: str) -> str:
    """
    Get the current weather for a given city using Open-Meteo.

    This tool ALWAYS looks up real data and never guesses temperatures.

    Args:
        city: City name, e.g. "Pune" or "Mumbai, IN".

    Returns:
        A concise human-readable description of the current weather, or a
        friendly error string if the city is not found or data is unavailable.
    """
    city_name = city.strip()
    if not city_name:
        return "Please provide a valid city name to look up the weather."

    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1) Geocode city to lat/lon
        try:
            geo_resp = await client.get(
                GEOCODE_URL,
                params={
                    "name": city_name,
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
            )
            geo_resp.raise_for_status()
        except Exception as exc:
            return f"Sorry, I couldn't reach the geocoding service: {exc}"

        data = geo_resp.json()
        results = data.get("results") or []
        if not results:
            return f"Sorry, I couldn't find weather data for '{city_name}'. Please check the city name and try again."

        first = results[0]
        lat = first.get("latitude")
        lon = first.get("longitude")
        resolved_name = first.get("name")
        country_code = first.get("country_code")

        if lat is None or lon is None:
            return f"Sorry, I couldn't determine coordinates for '{city_name}'."

        # 2) Fetch current weather
        try:
            weather_resp = await client.get(
                FORECAST_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True,
                    "temperature_unit": "celsius",
                    "windspeed_unit": "kmh",
                },
            )
            weather_resp.raise_for_status()
        except Exception as exc:
            return f"Sorry, I couldn't reach the weather service: {exc}"

        wdata = weather_resp.json()
        current = wdata.get("current_weather") or {}
        temperature = current.get("temperature")
        windspeed = current.get("windspeed")
        time = current.get("time")

        if temperature is None or windspeed is None or time is None:
            return f"Weather data for {resolved_name or city_name} is currently unavailable."

        location_label = (
            f"{resolved_name}, {country_code}" if country_code else resolved_name or city_name
        )

        return (
            f"Current weather for {location_label}: "
            f"{temperature}°C, wind {windspeed} km/h (as of {time})."
        )


