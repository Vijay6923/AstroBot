import requests
from geopy.geocoders import Nominatim
import os
from pathlib import Path

def geocode_city(city_name: str):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    return None

def fetch_weather(lat: float, lon: float):
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current_weather=true"
        f"&hourly=temperature_2m,precipitation,cloudcover,windspeed_10m,"
        f"apparent_temperature,relativehumidity_2m,weathercode,visibility,"
        f"shortwave_radiation,windgusts_10m,pressure_msl"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"windspeed_10m_max,windgusts_10m_max,sunrise,sunset"
        f"&timezone=auto"
    )
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def make_advisory(data: dict) -> str:
    """Turn JSON into plain English summary for LLM ingestion"""
    current = data.get("current_weather", {})
    daily = data.get("daily", {})

    temp = current.get("temperature", "N/A")
    wind = current.get("windspeed", "N/A")
    weather_code = current.get("weathercode", "N/A")

    # Extended fields with error handling
    try:
        max_temp = daily.get("temperature_2m_max", ["N/A"])[0]
        min_temp = daily.get("temperature_2m_min", ["N/A"])[0]
        rain = daily.get("precipitation_sum", ["N/A"])[0]
        max_wind = daily.get("windspeed_10m_max", ["N/A"])[0]
        max_gust = daily.get("windgusts_10m_max", ["N/A"])[0]
    except (IndexError, TypeError):
        max_temp = min_temp = rain = max_wind = max_gust = "N/A"

    summary = f"""
Current Weather:
- Temperature: {temp} °C
- Wind Speed: {wind} km/h
- Weather Code: {weather_code}

Daily Forecast:
- Max Temp: {max_temp} °C
- Min Temp: {min_temp} °C
- Rainfall (sum): {rain} mm
- Max Wind: {max_wind} km/h
- Max Gusts: {max_gust} km/h

Additional data available:
- Humidity, Radiation (Solar), Pressure, Visibility
- Can be used for advisories: Heat/Cold Waves, Cyclones, Rain, Solar/Wind, Sea State.
"""
    return summary

def save_weather_context(city: str):
    # Clear any existing weather data
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Remove existing weather context file
    weather_file = data_dir / "weather_context.txt"
    if weather_file.exists():
        weather_file.unlink()
    
    coords = geocode_city(city)
    if not coords:
        raise ValueError("City not found")
    
    lat, lon = coords
    data = fetch_weather(lat, lon)
    
    if not data:
        raise ValueError("Weather data fetch failed")

    advisory_text = make_advisory(data)
    
    with open(weather_file, "w", encoding="utf-8") as f:
        f.write(advisory_text)
    
    return str(weather_file)