import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
from enum import Enum


# Must take this data and process values:
# get swell Direction in 12 angles
# Get wind direction in twelve angles
# if wind direction is SE it is offshore wind for west strand
# if SW it is offshore for east strand.
# if wind is south and wind low swell could be good
# if wind is low and swell direction is NW could be good

# Based on these calculated values output a string that initially says if the swell is bummer, mid or gnarly
# followed by predicted conditions for what ever beach (offshore wind (wind direction), decent size (swell direction) good wind speed (wind speed) and whatever tide is (tide))

# Open Meteo is the best option (Take with grain of salt)

# This will only get today and tomorrow predictions
# It will only give certain times to make it easy for chatbotV1

# General Script will go Like:

# "Surf at beach_name is (description word of good/mid/bad surf) on date.
# Key times to surf time: wave_size, period, wind direction, wave_status (offshore)
# Do this for 9am, 2pm, 6pm

# Example in full
# Surf at west strand is looking hella gnarly on monday 25th may.
# Key times for kowabonga gotta be 9am with a wave size of 3ft, period of 11s wind direction of SE
# and status of Offshore


# Function to Convert date to Day Num Month (String) (Done)


# Function to put wave height to nearest .5 (1st dec place)
# Function to give in whol number (times by 1.5 open meteo is kind of awful for nc beaches)
# Function to convert 360 number (0 being North 90being east etc)
# Offshore Checker West Prefers (SE) East Prefers (SW) delve from this a little bit and it is Cross Offshore 
    # anything else just call 'messy yo'
# Function to compile sentence with all of this data and return it
# Amend function accept regex for surf, then determine if west or east strand are mentioned, if not
    # default to east strand



# Keep indexing below 48 as that is two days

# Getting started with config
# 1. Function to Convert date to Day Num Month (String)

def date2DDMM(dates):
    def get_suffix(day):
        if 11 <= day <= 13:
            return 'th'
        last_digit = day % 10
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(last_digit, 'th')

    def convert_hour(hour):
        if hour == 0:
            return '12am'
        elif hour < 12:
            return f'{hour}am'
        elif hour == 12:
            return '12pm'
        else:
            return f'{hour - 12}pm'

    formatted_dates = []
    for ts in dates[:48]:
        if not isinstance(ts, pd.Timestamp):
            ts = pd.to_datetime(ts)  # convert to pandas.Timestamp if needed

        day = ts.day
        suffix = get_suffix(day)
        month = ts.strftime('%B')  # full month name
        hour = ts.hour
        formatted_time = convert_hour(hour)

        formatted_str = f"{day}{suffix} of {month} {formatted_time}"
        formatted_dates.append(formatted_str)

    return formatted_dates


# Global Indexing Names
class SURF_IDX_NAMES(Enum):
    date = "date",
    wave_height = "wave_height",
    wave_period = "wave_period",
    wind_direction = "wind_wave_direction",
    wave_direction = "swell_wave_direction"


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
	"hourly": ["wave_height", "swell_wave_direction", "wave_period", "wind_wave_direction", "wave_peak_period"],
	"models": "best_match",
	"timezone": "Europe/London",
	"length_unit": "imperial",
	"wind_speed_unit": "mph",
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
    hourly_wave_direction = hourly.Variables(1).ValuesAsNumpy()
    hourly_wave_period = hourly.Variables(2).ValuesAsNumpy()
    hourly_wind_wave_direction = hourly.Variables(3).ValuesAsNumpy()


    hourly_data = {SURF_IDX_NAMES.date: pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}

    hourly_data[SURF_IDX_NAMES.wave_height] = hourly_wave_height # Eh round to nearest number then claim wave-+1 wave unless decimal was smaller than .2
    hourly_data[SURF_IDX_NAMES.wave_direction] = hourly_wave_direction
    hourly_data[SURF_IDX_NAMES.wave_period] = hourly_wave_period # Bad Prediction * 1.5 lol
    hourly_data[SURF_IDX_NAMES.wind_direction] = hourly_wind_wave_direction


    # hourly_dataframe = pd.DataFrame(data = hourly_data)
    print('first record of hourly data:')
    #print(hourly_data[SURF_IDX_NAMES.wave_height])

    # test first date
    print(date2DDMM(hourly_data[SURF_IDX_NAMES.date]))
    print(hourly_data[SURF_IDX_NAMES.date])
    # 9 is 8am  index -1 is actual time