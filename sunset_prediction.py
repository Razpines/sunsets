import datetime
import logging
import math
from zoneinfo import ZoneInfo

import pandas as pd
import requests

LAT = 32.07
LON = 34.78

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


def fetch_sunset_time(lat: float, lon: float) -> datetime.datetime:
    logging.info('Fetching sunset time')
    url = f'https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0'
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    sunset_utc = data['results']['sunset']
    sunset_dt = datetime.datetime.fromisoformat(sunset_utc.replace('Z', '+00:00'))
    local_tz = ZoneInfo('Asia/Jerusalem')
    return sunset_dt.astimezone(local_tz)


def fetch_weather(lat: float, lon: float) -> dict:
    logging.info('Fetching weather data from Open-Meteo')
    url = (
        'https://api.open-meteo.com/v1/forecast'
        f'?latitude={lat}&longitude={lon}'
        '&hourly=cloud_cover_high,cloud_cover_low,relative_humidity_700hPa'
        '&timezone=Asia%2FJerusalem'
    )
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def fetch_air_quality(lat: float, lon: float) -> dict:
    logging.info('Fetching air quality data from Open-Meteo')
    url = (
        'https://air-quality-api.open-meteo.com/v1/air-quality'
        f'?latitude={lat}&longitude={lon}'
        '&hourly=aerosol_optical_depth,dust,pm2_5'
        '&timezone=Asia%2FJerusalem'
    )
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def build_dataframe(weather: dict, aq: dict) -> pd.DataFrame:
    """Combine weather and air-quality data into a single DataFrame."""
    df_weather = pd.DataFrame(weather['hourly'])
    df_aq = pd.DataFrame(aq['hourly'])
    df = pd.merge(df_weather, df_aq, on='time')
    df['time'] = pd.to_datetime(df['time']).dt.tz_localize('Asia/Jerusalem')
    df.set_index('time', inplace=True)
    return df




def compute_score(row: pd.Series) -> float:
    """Compute a simple sunset score from a row of weather/AQ data."""
    high_cloud = row['cloud_cover_high']
    low_cloud = row['cloud_cover_low']
    rh700 = row['relative_humidity_700hPa']
    aod = row['aerosol_optical_depth']
    dust = row['dust']
    pm25 = row['pm2_5']

    w1 = w2 = w3 = w4 = w5 = w6 = 1
    score = (
        w1 * high_cloud
        - w2 * low_cloud
        + w3 * (rh700 - 40)
        - w4 * pm25
        + w5 * math.log(1 / abs(aod - 0.25))
        - w6 * dust
    )
    return score


def main():
    sunset_time = fetch_sunset_time(LAT, LON)
    weather = fetch_weather(LAT, LON)
    air_quality = fetch_air_quality(LAT, LON)

    df = build_dataframe(weather, air_quality)

    target_hour = sunset_time.replace(minute=0, second=0, microsecond=0)
    row = df.loc[target_hour]
    score = compute_score(row)

    print('Sunset time (local):', sunset_time)
    print('\nData table:')
    print(df)
    print('\nSunset score:', score)


if __name__ == '__main__':
    main()
