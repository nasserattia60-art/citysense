import requests
from statistics import mean

def get_weather_intelligence(lat: float, lon: float) -> dict:
    # ==============================
    # FETCH DATA
    # ==============================
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}"
        f"&longitude={lon}"
        "&forecast_days=14"
        "&current="
        "temperature_2m,relative_humidity_2m,apparent_temperature,"
        "precipitation,rain,snowfall,weather_code,cloud_cover,"
        "wind_speed_10m,wind_gusts_10m,pressure_msl,visibility,is_day"
        "&hourly="
        "temperature_2m,apparent_temperature,dew_point_2m,"
        "relative_humidity_2m,precipitation_probability,"
        "precipitation,rain,snowfall,snow_depth,freezing_level_height,"
        "cloud_cover,wind_speed_10m,wind_gusts_10m,pressure_msl,visibility"
        "&daily="
        "temperature_2m_max,temperature_2m_min,"
        "apparent_temperature_max,apparent_temperature_min,"
        "precipitation_sum,rain_sum,snowfall_sum,snow_depth_max,"
        "wind_speed_10m_max,wind_gusts_10m_max,uv_index_max"
        "&timezone=auto"
    )

    data = requests.get(url, timeout=15).json()

    # ==============================
    # HELPERS
    # ==============================
    kmh_to_ms = lambda x: round(x * 0.27778, 2)
    cm_to_mm = lambda x: round(x * 10, 1)

    # ==============================
    # STATISTICS
    # ==============================
    avg_temp = round(mean(data["daily"]["temperature_2m_max"]), 2)
    min_temp = min(data["daily"]["temperature_2m_min"])
    max_temp = max(data["daily"]["temperature_2m_max"])

    # ==============================
    # HUMAN FEELING
    # ==============================
    c = data["current"]
    feel = c["apparent_temperature"]
    humidity = c["relative_humidity_2m"]
    wind_kmh = c["wind_speed_10m"]

    status, color = "COMFORTABLE", "GREEN"
    if feel < -5 and wind_kmh > 25:
        status, color = "EXTREME_FREEZE", "RED"
    elif feel < 0:
        status, color = "FREEZING", "ORANGE"
    elif feel > 35 and humidity > 60:
        status, color = "HEAT_STRESS", "RED"

    # ==============================
    # SNOW ANALYSIS
    # ==============================
    daily = data["daily"]
    hourly = data["hourly"]

    total_snow_cm = sum(daily["snowfall_sum"])
    max_snow_depth = max(daily["snow_depth_max"])
    min_freezing_lvl = min(hourly["freezing_level_height"])

    snow_risk, snow_color = "LOW", "GREEN"
    if total_snow_cm > 5 or max_snow_depth > 10:
        snow_risk, snow_color = "MEDIUM", "ORANGE"
    if total_snow_cm > 20 or max_snow_depth > 30 or min_freezing_lvl < 400:
        snow_risk, snow_color = "HIGH", "RED"

    # ==============================
    # WEATHER RISK
    # ==============================
    min_visibility = min(hourly["visibility"])
    max_gusts = max(hourly["wind_gusts_10m"])
    min_pressure = min(hourly["pressure_msl"])

    risk, risk_color = "NORMAL", "GREEN"
    if min_visibility < 800 or max_gusts > 60:
        risk, risk_color = "DANGEROUS", "ORANGE"
    if min_visibility < 300 or (min_pressure < 995 and max_gusts > 70):
        risk, risk_color = "EXTREME", "RED"

    # ==============================
    # FINAL BUSINESS JSON
    # ==============================
    return {
        "location": {
            "latitude": lat,
            "longitude": lon,
            "timezone": data.get("timezone")
        },
        "statistics": {
            "avg_temperature_14_days_C": avg_temp,
            "min_14_days_C": min_temp,
            "max_14_days_C": max_temp
        },
        "human_feeling_index": {
            "apparent_temperature_C": feel,
            "humidity_percent": humidity,
            "wind_speed_kmh": wind_kmh,
            "wind_speed_ms": kmh_to_ms(wind_kmh),
            "status": status,
            "status_color": color
        },
        "snow_analysis": {
            "total_snow_cm": total_snow_cm,
            "total_snow_mm": cm_to_mm(total_snow_cm),
            "max_snow_depth_cm": max_snow_depth,
            "freezing_level_min_m": min_freezing_lvl,
            "risk_level": snow_risk,
            "risk_color": snow_color
        },
        "weather_risk_engine": {
            "min_visibility_m": min_visibility,
            "max_wind_gusts_kmh": max_gusts,
            "max_wind_gusts_ms": kmh_to_ms(max_gusts),
            "min_pressure_hpa": min_pressure,
            "risk_level": risk,
            "risk_color": risk_color
        }
    }
