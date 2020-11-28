import requests
from actions.Action import Action

# Get your API key from https://openweathermap.org/home/sign_up
FORECAST_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric'
NO_CITY = 'I could not find a city'
NO_APPID = 'There is no openweathermap app id that I could use'

responses = {
    'de': {
        'NO_CITY': 'Um das Wetter nachzusehen benötige ich eine Stadt. Leider konnte ich aus deiner Anfrage keine Stadt herauslesen.',
        'NO_APPID': 'Zur Zeit ist keine openweathermap App-Id hinterlegt'
    },
    'en': {
        'NO_CITY': 'I need a city to check the weather. Unfortunately I could not find a city in your request.',
        'NO_APPID': 'There is no openweathermap app id configured that I could use'
    }
}

class OpenWeatherAction(Action):
    name = "Weather"
    description = """
    OpenWeather action. Forecast for a city
    """.strip()

    def __init__(self, settings={}):
        self.name = OpenWeatherAction.name
        self.description = OpenWeatherAction.description
        super().__init__(settings)

    def execute(self, query, intent=None, extra={}):
        language = extra['language']

        if 'appid' not in self.settings:
            return responses[language]['NO_APPID']
        
        if 'cities' not in extra['data_collection']:
            return responses[language]['NO_CITY']
        elif not extra['data_collection']['cities']:
            return responses[language]['NO_CITY']

        city = extra['data_collection']['cities'][0]

        appid = self.settings['appid']
        response = requests.get(FORECAST_URL.format(city, appid)).json()
        if extra['language'] == 'de':
            description = f"In {city} ist es zur Zeit {response['main']['temp']}C " \
                + f"mit {response['weather'][0]['description']} " \
                + f"und einer gefühlten Temperatur von {response['main']['feels_like']}C. "
        else:
            description = f"The weather in {city} is {response['main']['temp']}C " \
                + f"with {response['weather'][0]['description']} " \
                + f"and feels like {response['main']['feels_like']}C. "
        return description
