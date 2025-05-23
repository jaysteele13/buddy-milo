# give the string as parameter

# before using the llm for general trained buddy talk look for key words

# Surf
# Check surf in west strand and east strand portrush

# Weather -> check weather in Portrush

# 'Milk' -> yes, my milk is delicious

# 'Beatbox' play .wav of beatbox.wav

# Anything else process in LLM 'Using Big Brain'


# Series of Regex and If statements

# def possible_words(word):
    # [reg word[i] word in order]
    #   word phentically
    # word with different vowel

import re
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests

# use bbc weather for weather
def weather_forecast():
    return













# Must take this data and process values:
# get swell Direction in 12 angles
# Get wind direction in twelve angles
# if wind direction is SE it is offshore wind for west strand
# if SW it is offshore for east strand.
# if wind is south and wind low swell could be good
# if wind is low and swell direction is NW could be good

# Based on these calculated values output a string that initially says if the swell is bummer, mid or gnarly
# followed by predicted conditions for what ever beach (offshore wind (wind direction), decent size (swell direction) good wind speed (wind speed) and whatever tide is (tide))

# Using Open_meteo API for Surf
def surf_forecast():
    # WAVE DIRECTION

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://marine-api.open-meteo.com/v1/marine"

    west_strand_lat = 55.201625
    west_strand_lng = -6.660911

    east_strand_lat = 55.208025
    east_strand_lng = -6.643585

    params = {
        "latitude": west_strand_lat,
        "longitude": west_strand_lng,
        "hourly": ["wave_height", "swell_wave_direction", "wave_period"],
        "length_unit": "imperial",
        "wind_speed_unit": "mph"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_wave_height = hourly.Variables(0).ValuesAsNumpy()
    hourly_swell_wave_direction = hourly.Variables(1).ValuesAsNumpy()
    hourly_wave_period = hourly.Variables(2).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["wave_height"] = hourly_wave_height
    hourly_data["swell_wave_direction"] = hourly_swell_wave_direction
    hourly_data["wave_period"] = hourly_wave_period

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    print(hourly_dataframe)

    ## WIND DIRECTION

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": west_strand_lat,
        "longitude": west_strand_lng,
        "hourly": ["temperature_2m", "wind_direction_10m", "wind_direction_120m"],
        "current": "wind_speed_10m",
        "wind_speed_unit": "mph"
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_wind_speed_10m = current.Variables(0).Value()

    print(f"Current time {current.Time()}")
    print(f"Current wind_speed_10m {current_wind_speed_10m}")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_wind_direction_10m = hourly.Variables(1).ValuesAsNumpy()
    hourly_wind_direction_120m = hourly.Variables(2).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["wind_direction_10m"] = hourly_wind_direction_10m
    hourly_data["wind_direction_120m"] = hourly_wind_direction_120m

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    print(hourly_dataframe)


def check_for_main_prompt(sentence):
    sentence = sentence.lower()

    if re.search(r'\b(surf|serf)\b', sentence):
        return surf_forecast()
    elif re.search(r'\bweather\b', sentence):
        return 'weather_forecast()'
    elif re.search(r'\bmilk\b', sentence):
        return 'my milk is delicious'
    else:
        return 'lama_llm(sentence)'
    

if __name__ == "__main__":

    sentence = 'i needa surf right now'
    print(check_for_main_prompt(sentence))


