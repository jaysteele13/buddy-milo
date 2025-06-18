import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
from enum import Enum
import numpy as np
import random

def convert_hour(hour):
        if hour == 0:
            return '12am'
        elif hour < 12:
            return f'{hour}am'
        elif hour == 12:
            return '12pm'
        else:
            return f'{hour - 12}pm'
def date2DDMM(dates):
    def get_suffix(day):
        if 11 <= day <= 13:
            return 'th'
        last_digit = day % 10
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(last_digit, 'th')


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

# 2. Function to put wave height to nearest .5 (1st dec place)
def waveHeightToNearestDec(waveHeights):
    # Use numpy's round function to round to nearest 0.5
    rounded = np.round(waveHeights * 2) / 2
    return rounded

# Function to give period in whol number (times by 1.5 open meteo is kind of awful for nc beaches)
def wavePeriodToSeconds(wavePeriods):
    rounded = np.round(wavePeriods)
    rounded *= 1.5
    return rounded

# 4. Function to convert 360 number (0 being North 90being east etc)
def mapDegreeToDirection(directions):
    new_directions = []
    dirs = ['North', 'North North East', 'North East', 'East North East', 'East', 'East South East', 'South East', 'South South East', 
            'South', 'South South West', 'South West', 'West South West', 'West', 'West North West', 'North West', 'North North West']
    
    for deg in directions:
        ix = round(deg / (360. / len(dirs))) % len(dirs)
        new_directions.append(dirs[ix])
    
    return new_directions

def offshoreChecker(directions, beach):
    new_status = []

    for deg in directions:
        if beach == BEACH_NAMES.west_strand.value:
            if deg in ['South East', 'South South East']:
                new_status.append('Offshore')
            elif deg == 'South':
                new_status.append('Cross Offshore')
            else:
                new_status.append('Onshore')

        elif beach == BEACH_NAMES.east_strand.value:
            if deg in ['South West', 'South South West']:
                new_status.append('Offshore')
            elif deg == 'South':
                new_status.append('Cross Offshore')
            else:
                new_status.append('Onshore')

    return new_status
def decorate_wind_status(statuses):
    andy_good = [
        'Disco Biscuits', 'Pumpasaurous Rex', 'Chunkie on er', 'its pumping',
        "Offshore, as predicted by c'est moi", "lovely right handers", "dorris approves",
        "pumping with a side of Roasting-a-saurous-rex", "surfs up you toads", "clean", "fun wee waves",
        "styling, keep her lit... lovely", "there is motion in the ocean", "there is motion in the ocean", "clean"
    ]
    andy_bad = [
        'No Swellers', 'Skeleton Crew in Water', 'These waves are shit',
        "dorris doesn't approve", "death of the swell, top up our tans", "disappointing", "no minky whales", "tracks in the sand, where will they lead to?, unfortunetely, not too good surf", 
    ]
    andy_mid = ["hint of swell", "enough to learn on...", "a bit lumpy", "its mid brother"]

    decorated = []
    for status in statuses:
        if status == WAVE_STATUS.good.value:
            decorated.append(random.choice(andy_good))
        elif status == WAVE_STATUS.mid.value:
            decorated.append(random.choice(andy_mid))
        else:
            decorated.append(random.choice(andy_bad))
    return decorated



# 6. Function to declare if surf is 'gnarly' 'mid' or 'trash'
def surf_status(wave_size, wave_period, wind_direction_status):
    preferred_wave_size_min = 3.0
    preferred_wave_size_max = 6.0
    preferred_wave_period_min = 10
    preferred_w_status = 'Offshore'

    statuses = []

    for i in range(len(wave_size)):
        if (preferred_wave_size_min <= wave_size[i] <= preferred_wave_size_max and
            wave_period[i] >= preferred_wave_period_min and
            wind_direction_status[i] == preferred_w_status):
            statuses.append(WAVE_STATUS.good.value)
        elif (2 <= wave_size[i] < preferred_wave_size_min and
              wave_period[i] >= preferred_wave_period_min and
              (wind_direction_status[i] == 'Cross Offshore' or wind_direction_status[i] == 'Offshore' )):
            statuses.append(WAVE_STATUS.mid.value)
        else:
            statuses.append(WAVE_STATUS.bad.value)

    return statuses

# "Surf at beach_name is (description word of good/mid/bad surf) on date.
# Key times to surf time: wave_size, period, wind direction, wave_status (offshore)
# Do this for 9am, 2pm, 6pm

# Example in full
# Surf at west strand is looking hella gnarly on monday 25th may.
# Key times for kowabonga gotta be 9am with a wave size of 3ft, period of 11s wind direction of SE
# and status of Offshore
def build_stats(wave_size, wave_period, wind_direction, wind_status, time_idx):
    return f"{convert_hour(time_idx)} with a wave size of {wave_size} feet, period of {wave_period} seconds, wind direction of {wind_direction} and a wave status of {wind_status}. "

def compile_sentence(wave_size, wave_period, wind_direction, wave_status, date, beach, today, andy_phrases):

    def remove_time_from_date(date_str):
        # Assumes format like "28 May 2pm"
        parts = date_str.split()
        return " ".join(parts[:3])

    # idx for times
    # Today, tommorow? +24
    tom_multiplier = 0 if today else 24
    nine_am = 10 + tom_multiplier 
    two_pm = 15 + tom_multiplier
    six_pm = 19 + tom_multiplier

    new_date = remove_time_from_date(date[nine_am])

    if (wave_status[nine_am] == WAVE_STATUS.mid.value) or (wave_status[two_pm] == WAVE_STATUS.mid.value) or (wave_status[six_pm] == WAVE_STATUS.mid.value):
        wave_status = WAVE_STATUS.mid.value
    elif (wave_status[nine_am] == WAVE_STATUS.good.value) or (wave_status[two_pm] == WAVE_STATUS.good.value) or (wave_status[six_pm] == WAVE_STATUS.good.value):
        wave_status = WAVE_STATUS.good.value
    else:
        wave_status = WAVE_STATUS.bad.value

    sentence = (
        f"Surf at {beach} is looking hella {wave_status} {'today' if today else 'tomorrow'}, date being, {new_date}. "
        f"Key times to surf are the following. "
        f"{build_stats(wave_size=wave_size[nine_am], wave_period=wave_period[nine_am], wind_direction=wind_direction[nine_am], wind_status=andy_phrases[nine_am], time_idx=9)}"
        f"{build_stats(wave_size=wave_size[two_pm], wave_period=wave_period[two_pm], wind_direction=wind_direction[two_pm], wind_status=andy_phrases[two_pm], time_idx=14)}"
        f"{build_stats(wave_size=wave_size[six_pm], wave_period=wave_period[six_pm], wind_direction=wind_direction[six_pm], wind_status=andy_phrases[six_pm], time_idx=18)}"
    )

    return sentence

class WAVE_STATUS(Enum):
    good = "gnarly",
    mid = "mid",
    bad = "trash"

class BEACH_NAMES(Enum):
    west_strand = "West Strand",
    east_strand = "East Strand"


# Global Indexing Names
class SURF_IDX_NAMES(Enum):
    date = "date",
    wave_height = "wave_height",
    wave_period = "wave_period",
    wind_direction = "wind_wave_direction",
    wave_direction = "swell_wave_direction"


# Using Open_meteo API for Surf
def surf_forecast(beach = BEACH_NAMES.east_strand.value, today = True):
    # WAVE DIRECTION

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://marine-api.open-meteo.com/v1/marine"

    lat = 0 # declare values
    lng = 0

    if beach == BEACH_NAMES.east_strand.value:
        lat = 55.208025 # East coords
        lng = -6.643585
    else:
        lat = 55.201625 # West coords
        lng = -6.660911

    params = {
	"latitude": lat,
	"longitude": lng,
	"hourly": ["wave_height", "swell_wave_direction", "wave_period", "wind_wave_direction", "wave_peak_period"],
	"models": "best_match",
	"timezone": "Europe/London",
	"length_unit": "imperial",
	"wind_speed_unit": "mph",
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]

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

    # 1. test first date
    # print(date2DDMM(hourly_data[SURF_IDX_NAMES.date]))
    # print(hourly_data[SURF_IDX_NAMES.date])
    # 9 is 8am  index -1 is actual time
    dates = date2DDMM(hourly_data[SURF_IDX_NAMES.date])


    # 2. Wave Height Decimal
    # print(waveHeightToNearestDec(hourly_data[SURF_IDX_NAMES.wave_height]))
    waveHeights = waveHeightToNearestDec(hourly_data[SURF_IDX_NAMES.wave_height])
    # print(waveHeight)

    # 3 Wave Period to whole number with calculation of 1.5
    # print(wavePeriodToSeconds(hourly_data[SURF_IDX_NAMES.wave_period]))
    wavePeriods = wavePeriodToSeconds(hourly_data[SURF_IDX_NAMES.wave_period])
    # print(wavePeriod)

    # 4 Function to convert wind 360 number (0 being North 90being east etc)
    # print(mapDegreeToDirection(hourly_data[SURF_IDX_NAMES.wind_direction]))
    windDirections = mapDegreeToDirection(hourly_data[SURF_IDX_NAMES.wind_direction])
    # print(windDirections)

    # 5 Offshore checker
    # print(offshoreChecker(mapDegreeToDirection(hourly_data[SURF_IDX_NAMES.wind_direction]), BEACH_NAMES.east_strand.value))
    windStatus = offshoreChecker(windDirections, beach)


    # 6: Wave Status
    waveStatus = surf_status(wave_size= waveHeights, 
                      wave_period=wavePeriods,
                       wind_direction_status=windStatus )
    
    andy_phrases = decorate_wind_status(waveStatus)

   
    # 7. Return Compiled Sentence
    return compile_sentence(wave_size=waveHeights, wave_period=wavePeriods, wind_direction=windDirections, wave_status=waveStatus, date=dates, andy_phrases=andy_phrases
                            ,beach=beach, today=today)
