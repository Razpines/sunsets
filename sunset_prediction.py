import datetime
import logging
import math
import requests

LAT = 32.07
LON = 34.78

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')


def fetch_sunset_time(lat: float, lon: float) -> datetime.datetime:
    logging.debug('Fetching sunset time')
    url = f'https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0'
    resp = requests.get(url)
    logging.debug('Sunrise-sunset response: %s', resp.text)
    resp.raise_for_status()
    data = resp.json()
    sunset_utc = data['results']['sunset']
    sunset_dt = datetime.datetime.fromisoformat(sunset_utc.replace('Z', '+00:00'))
    logging.debug('Sunset time (UTC): %s', sunset_dt)
    return sunset_dt


def fetch_weather(lat: float, lon: float) -> dict:
    logging.debug('Fetching weather data from Open-Meteo')
    url = (
        'https://api.open-meteo.com/v1/forecast'
        f'?latitude={lat}&longitude={lon}'
        '&hourly=cloud_cover_high,cloud_cover_low,relative_humidity_700hPa'
        '&timezone=UTC'
    )
    resp = requests.get(url)
    logging.debug('Open-Meteo weather response: %s', resp.text[:200])
    resp.raise_for_status()
    return resp.json()


def fetch_air_quality(lat: float, lon: float) -> dict:
    logging.debug('Fetching air quality data from Open-Meteo')
    url = (
        'https://air-quality-api.open-meteo.com/v1/air-quality'
        f'?latitude={lat}&longitude={lon}'
        '&hourly=aerosol_optical_depth,dust,pm2_5'
        '&timezone=UTC'
    )
    resp = requests.get(url)
    logging.debug('Open-Meteo AQ response: %s', resp.text[:200])
    resp.raise_for_status()
    return resp.json()




def compute_score(weather: dict, aq: dict, target_hour: datetime.datetime) -> tuple[float, dict]:
    logging.debug('Computing sunset score')
    hourly = weather['hourly']
    target_str = target_hour.strftime('%Y-%m-%dT%H:00')
    idx = hourly['time'].index(target_str)
    high_cloud = hourly['cloud_cover_high'][idx]
    low_cloud = hourly['cloud_cover_low'][idx]
    rh700 = hourly['relative_humidity_700hPa'][idx]

    aq_hourly = aq['hourly']
    aq_idx = aq_hourly['time'].index(target_str)
    aod = aq_hourly['aerosol_optical_depth'][aq_idx]
    dust = aq_hourly['dust'][aq_idx]
    pm25 = aq_hourly['pm2_5'][aq_idx]

    # simple weights
    w1, w2, w3, w4, w5, w6 = 1, 1, 1, 1, 1, 1
    score = (
        w1 * high_cloud
        - w2 * low_cloud
        + w3 * (rh700 - 40)
        - w4 * pm25
        + w5 * math.log(1 / abs(aod - 0.25))
        - w6 * dust
    )
    logging.debug(
        'Variables -> high_cloud=%s low_cloud=%s rh700=%s pm25=%s aod=%s dust=%s',
        high_cloud,
        low_cloud,
        rh700,
        pm25,
        aod,
        dust,
    )
    variables = {
        "high_cloud": high_cloud,
        "low_cloud": low_cloud,
        "rh700": rh700,
        "pm25": pm25,
        "aod": aod,
        "dust": dust,
    }
    return score, variables


def main():
    sunset_time = fetch_sunset_time(LAT, LON)
    weather = fetch_weather(LAT, LON)
    air_quality = fetch_air_quality(LAT, LON)

    # choose hour nearest to sunset
    target_hour = sunset_time.replace(minute=0, second=0, microsecond=0)
    score, variables = compute_score(weather, air_quality, target_hour)
    aq_hourly = air_quality['hourly']
    target_str = target_hour.strftime('%Y-%m-%dT%H:00')
    aq_idx = aq_hourly['time'].index(target_str)
    pm25 = aq_hourly['pm2_5'][aq_idx]

    print('Sunset time (UTC):', sunset_time)
    print('Weather data sample:', weather['hourly']['time'][:3])
    print('Air quality sample:', air_quality['hourly']['time'][:3])
    print('PM2.5:', pm25)
    print('Variables:', variables)
    print('Sunset score:', score)


if __name__ == '__main__':
    main()
