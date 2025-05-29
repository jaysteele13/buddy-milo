import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry
import numpy as np
from weather_codes import weather_codes
from enum import Enum

def NumToWhole(temp):
    rounded = np.round(temp)
    return rounded

# Function to gather temps from 6am to 8pm and get average
def averageSix2Eight(data):
    sixAmIdx = 7
    eightPmIdx = 19

    # Grabs temps from 7 to 19 (i.e., 6 AM to 8 PM)
    avg = 0
    for i in range(sixAmIdx, eightPmIdx + 1):
        avg += data[i]
    
    avg = avg / (eightPmIdx - sixAmIdx + 1)
    return avg

def get_weather_code(code):
    if code > len(weather_codes):
        return 'not sure'
    else:
        return weather_codes[code]
    
def get_precipitation(rain, shower, hail, snow):
    final_idx = 24  # or min(len(...)) if arrays may be shorter
    precips = []
    
    for i in range(final_idx):
        if snow[i] > 0:
             precips.append(precip_codes.snow.value)
        elif hail[i] > 0:
             precips.append(precip_codes.hail.value)
        elif shower[i] > 0:
             precips.append(precip_codes.shower.value)
        elif rain[i] > 0:
             precips.append(precip_codes.rain.value)
        else:
            precips.append(precip_codes.clear.value)

    return precips


def extract_hours_minutes(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    parts = []
    if hours > 0:
        hour_label = "hour" if hours == 1 else "hours"
        parts.append(f"{hours} {hour_label}")
    if minutes > 0 or not parts:
        minute_label = "minute" if minutes == 1 else "minutes"
        parts.append(f"{minutes} {minute_label}")

    return " and ".join(parts)


# Weather in Portrush today has an avg temperature of X. In the morning the temperature will be around X with a weather status of X, midday the temp will X with status of X humidity also
# in the evening it will be etc
def compile_sentence(all_temp, avg_temp, wind_avg, amount_of_sun, codes, humidity, precipitation):
    nine_am = 10  
    two_pm = 15 
    six_pm = 19

    parts = []

    # Core weather summary
    parts.append(f"The average temperature today in Portrush is {avg_temp}°C.")
    parts.append(f"With the average wind speed being {wind_avg} mph.")

    # Sunshine info
    if len(amount_of_sun) > 0:
        parts.append(f"Expect to see sunshine for {amount_of_sun} today yo.")

    

    # Time-specific observations
    parts.append(f"In the morning, Portrush is {all_temp[nine_am]}°C and '{get_weather_code(codes[nine_am])}'.")
    parts.append(f"By midday, it is {all_temp[two_pm]}°C and '{get_weather_code(codes[two_pm])}'.")

    # Stickiness from humidity
    if humidity[two_pm] > 65:
        parts.append(f"This midday air is feeling pretty sticky with humidity at {humidity[two_pm]}")

    parts.append(f"In the evening, it is {all_temp[six_pm]}°C and '{get_weather_code(codes[six_pm])}'.")

    if precipitation[nine_am] != precip_codes.clear.value:
        parts.append(f"Expecting morning: {precipitation[nine_am]}")

    if precipitation[nine_am] != precip_codes.clear.value:
        parts.append(f"Expecting midday: {precipitation[two_pm]}")

    if precipitation[nine_am] != precip_codes.clear.value:
        parts.append(f"Expecting evening: {precipitation[six_pm]}")

    return " ".join(parts)




class precip_codes(Enum):
    clear = "clear",
    rain = "rain",
    shower = "showers",
    hail = "hail",
    snow = "snow"


def weather_forecast():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 55.199185,
        "longitude": -6.652579,
        "daily": "sunshine_duration",
        "hourly": ["temperature_2m", "weather_code", "precipitation", "rain", "showers", "snowfall", "hail", 'relative_humidity_2m', 'wind_speed_10m'],
        "models": "ukmo_seamless",
        "timezone": "Europe/London",
        "wind_speed_unit": "mph"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_weather_code = hourly.Variables(1).ValuesAsNumpy()
    hourly_rain = hourly.Variables(3).ValuesAsNumpy()
    hourly_showers = hourly.Variables(4).ValuesAsNumpy()
    hourly_snowfall = hourly.Variables(5).ValuesAsNumpy()
    hourly_hail = hourly.Variables(6).ValuesAsNumpy()
    hourly_humidity = hourly.Variables(7).ValuesAsNumpy()
    hourly_wind_speed = hourly.Variables(8).ValuesAsNumpy()
   
    wind_speed = NumToWhole(hourly_wind_speed)
    wind_speed_avg = NumToWhole(averageSix2Eight(wind_speed))

    # print(hourly_dataframe)
    temps = NumToWhole(hourly_temperature_2m)
    # print(f'temps: {temps}')

    daily = response.Daily()
    daily_sunshine_duration = daily.Variables(0).ValuesAsNumpy()


    # Function to gather temps from 6am to 8pm and get average
    temp_avg = NumToWhole(averageSix2Eight(temps))
    # print(f'print avg temp: {temp_avg}')

    # Function to output string based on weather code
    cleaned = np.nan_to_num(hourly_weather_code, nan=-1).astype(np.int64)
    weather_codes = cleaned.astype(np.int64)
    # print(f'here is a weather code {get_weather_code(weather_codes[8])}')

    # Function to take in precip and output the highest value with prioritisation
    precipitation_today = get_precipitation(hourly_rain, hourly_showers,  hourly_hail, hourly_snowfall)
    # print(f"precip today: {precipitation_today}")

    # Global index within 24
    amount_of_sun = extract_hours_minutes(NumToWhole(daily_sunshine_duration[0]))
    # print(f'amount of sun: {amount_of_sun  }')

    return compile_sentence(temps, temp_avg, wind_speed_avg, amount_of_sun, weather_codes,hourly_humidity,precipitation_today)

