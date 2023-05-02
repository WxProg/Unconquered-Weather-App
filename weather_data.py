import os
import requests
from dotenv import load_dotenv
import urllib.parse

load_dotenv(dotenv_path='.env')
api_key = os.getenv('omwApiKey')


# Open Weather Map - Weather Data
def get_weather_data(city_name, state_code):
    owm_w_url = f'https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(string=city_name)},' \
                f'us-{state_code}&appid={api_key}'
    w_response = requests.get(url=owm_w_url)
    w_response.raise_for_status()
    w_data = w_response.json()

    return w_data


# Open Weather Map - Air Pollution Data
def get_ap_data(city_lat, city_lon):
    owm_ap_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={city_lat}&lon={city_lon}&appid={api_key}'
    ap_response = requests.get(url=owm_ap_url)
    ap_response.raise_for_status()
    ap_data = ap_response.json()

    return ap_data
