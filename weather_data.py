import os
import requests
from dotenv import load_dotenv
import urllib.parse

load_dotenv(dotenv_path='.env')
api_key = os.getenv('omwApiKey')

# This is a mapping from OpenWeatherMap's weather conditions to Font Awesome icon classes.
# It will be used to replace OpenWeatherMap's default weather condition icons.
icon_map = {
    '01d': 'fa-solid fa-sun fa-lg',            # clear sky (day)
    '01n': 'fa-solid fa-moon fa-lg',           # clear sky (night)
    '02d': 'fa-solid fa-cloud-sun fa-lg',      # few clouds (day)
    '02n': 'fa-solid fa-cloud-moon fa-lg',     # few clouds (night)
    '03d': 'fa-solid fa-cloud fa-lg',          # scattered clouds (day)
    '03n': 'fa-solid fa-cloud fa-lg',          # scattered clouds (night)
    '04d': 'fa-solid fa-cloud fa-lg',         # broken clouds (day)
    '04n': 'fa-solid fa-cloud fa-lg',         # broken clouds (night)
    '09d': 'fa-solid fa-cloud-showers-heavy fa-lg',  # shower rain (day)
    '09n': 'fa-solid fa-cloud-showers-heavy fa-lg',  # shower rain (night)
    '10d': 'fa-solid fa-cloud-sun-rain fa-lg', # rain (day)
    '10n': 'fa-solid fa-cloud-moon-rain fa-lg',# rain (night)
    '11d': 'fa-solid fa-cloud-bolt fa-lg',   # thunderstorm (day)
    '11n': 'fa-solid fa-cloud-bolt fa-lg',   # thunderstorm (night)
    '13d': 'fa-solid fa-snowflake fa-lg',     # snow (day)
    '13n': 'fa-solid fa-snowflake fa-lg',     # snow (night)
    '50d': 'fa-solid fa-fog fa-lg',            # mist/fog (day)
    '50n': 'fa-solid fa-fog fa-lg',            # mist/fog (night)
}
# Extracting specific parts of the Weather Data
def extract_weather_data(weather_data):
    icon_code = weather_data['weather'][0]['icon']
    # the icon map is to convert icon_code to a Font Awesome class
    # in case of an unknown icon_code, a default is used.
    icon_class = icon_map.get(icon_code, 'fas fa-question-circle')

    # Convert visibility from meters to kilometers and truncate to 1 decimal places
    visibility_in_km = weather_data['visibility'] /1000
    truncated_visibility = round(visibility_in_km, 1)

    return {
        'temperature': weather_data['main']['temp'],
        'max_temp': weather_data['main']['temp_max'],
        'min_temp': weather_data['main']['temp_min'],
        'humidity': weather_data['main']['humidity'],
        'description': weather_data['weather'][0]['description'],
        'description_icon': icon_code,
        'description_icon_url': icon_class,
        'pressure': weather_data['main']['pressure'],
        'visibility': truncated_visibility,
        'city_name': weather_data['name'],
        'wind_speed': weather_data['wind']['speed']
    }


# Open Weather Map - Weather Data
def get_weather_data(city_name, state_code):
    owm_w_url = f'https://api.openweathermap.org/data/2.5/weather?q={urllib.parse.quote(string=city_name)},' \
                f'us-{state_code}&appid={api_key}&units=imperial'
    w_response = requests.get(url=owm_w_url)
    w_response.raise_for_status()
    w_data = w_response.json()

    return extract_weather_data(w_data)


# Open Weather Map - Air Pollution Data
def get_ap_data(city_lat, city_lon):
    owm_ap_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={city_lat}&lon={city_lon}&appid={api_key}'
    ap_response = requests.get(url=owm_ap_url)
    ap_response.raise_for_status()
    ap_data = ap_response.json()

    return ap_data
