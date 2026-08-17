import requests


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",

    45: "Fog",
    48: "Depositing rime fog",

    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",

    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",

    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",

    66: "Light freezing rain",
    67: "Heavy freezing rain",

    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",

    77: "Snow grains",

    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",

    85: "Slight snow showers",
    86: "Heavy snow showers",

    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


# =========================================================
# GEOCODING
# =========================================================

def get_coordinates(
    place_name,
    state=None,
    country=None
):
    """
    Automatically find latitude and longitude.

    No coordinates need to be entered by the user.
    """

    url = (
        "https://geocoding-api.open-meteo.com"
        "/v1/search"
    )

    # Try the most specific search first
    search_name = place_name

    if state and country:
        search_name = (
            f"{place_name}, {state}, {country}"
        )

    elif country:
        search_name = (
            f"{place_name}, {country}"
        )

    params = {
        "name": search_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    # If specific search fails, try just place name
    if not data.get("results"):

        params["name"] = place_name

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

    if not data.get("results"):
        raise ValueError(
            f"Location '{place_name}' not found"
        )

    result = data["results"][0]

    return {
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "timezone": result.get(
            "timezone",
            "auto"
        ),
        "country": result.get(
            "country",
            country
        ),
        "state": result.get(
            "admin1",
            state
        )
    }


# =========================================================
# WEATHER
# =========================================================

def get_weather(city_name):

    location = get_coordinates(
        city_name
    )

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "weather_code"
        ),
        "timezone": location["timezone"]
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    current = data["current"]

    weather_code = current["weather_code"]

    return {
        "city_name": city_name,
        "state": location["state"],
        "country": location["country"],

        "latitude": location["latitude"],
        "longitude": location["longitude"],

        "temperature": current[
            "temperature_2m"
        ],

        "humidity": current[
            "relative_humidity_2m"
        ],

        "weather_condition": WEATHER_CODES.get(
            weather_code,
            "Unknown"
        ),

        "recorded_at": current["time"]
    }