from dtos.location import Location
from datetime import datetime
import json
import sys
import requests

class OpenWeatherService:
	API_KEY = ''
	historic_url = 'https://api.openweathermap.org/data/2.5/onecall/timemachine?'
	onecall_url = 'https://api.openweathermap.org/data/2.5/onecall?'
	HPA_TO_INHG= 0.03
	M_TO_MI = 0.000621371192
	MM_TO_INCH = 0.0393700787

	def __init__(self, API_KEY):
		self.API_KEY = API_KEY


	def getWeather(self, location, selected_time, current_time):
		weather_data = []
		#Get weather data
		if selected_time < current_time:
			#Get historical data
			weather_data = self.getHistoricalData(location, selected_time)
			if (weather_data == None):
				return None
		elif selected_time == current_time:
			#Get current weather
			weather_data = self.getCurrentData(location)
			if (weather_data == None):
				return None
		else:
			#Get forecast
			weather_data = self.getForecastData(location, selected_time)
			if (weather_data == None):
				return None
		return weather_data

	def getHistoricalData(self, location, time):
		weather_data = []

		params = {
			'lat': location.lat,
			'lon': location.lng,
			'dt': time.strftime('%s'),
			'appid': self.API_KEY,
			'units': 'imperial'
		}

		response = requests.get(self.historic_url, params=params)
		print(json.dumps(response.json()), file=sys.stderr)
		if (response):
			data = response.json()['current']
			weather_data.append(data['temp'])
			weather_data.append(data['humidity'])
			weather_data.append(data['pressure'] * self.HPA_TO_INHG)
			weather_data.append(data['visibility'] * self.M_TO_MI)
			weather_data.append(data['wind_speed'])
			if ('rain' in data and '1h' in data['rain']):
				weather_data.append(data['rain']['1h'] * self.MM_TO_INCH)
			else:
				weather_data.append(0.009854445520487937)
			return weather_data

		return None

	def getCurrentData(self, location):
		weather_data = []

		params = {
			'lat': location.lat,
			'lon': location.lng,
			'exclude': 'minutely,hourly,daily,alerts',
			'appid': self.API_KEY
		}

		response = requests.get(self.onecall_url, params=params)
		print(json.dumps(response.json()), file=sys.stderr)
		if (response):
			data = response.json()['current']
			weather_data.append(data['temp'])
			weather_data.append(data['humidity'])
			weather_data.append(data['pressure'] * self.HPA_TO_INHG)
			weather_data.append(data['visibility'] * self.M_TO_MI)
			weather_data.append(data['wind_speed'])
			if ('rain' in data and '1h' in data['rain']):
				weather_data.append(data['rain']['1h'] * self.MM_TO_INCH)
			else:
				weather_data.append(0.009854445520487937)
			return weather_data

		return None

	def getForecastData(self, location, time):
		weather_data = []

		params = {
			'lat': location.lat,
			'lon': location.lng,
			'exclude': 'current,minutely,daily,alerts',
			'appid': self.API_KEY
		}

		response = requests.get(self.onecall_url, params=params)
		print(json.dumps(response.json()), file=sys.stderr)
		if (response):
			for data in response.json()['hourly']:
				forecast_time = datetime.fromtimestamp(data['dt'])
				if (time.day == forecast_time.day and time.hour == forecast_time.hour):
					weather_data.append(data['temp'])
					weather_data.append(data['humidity'])
					weather_data.append(data['pressure'] * self.HPA_TO_INHG)
					weather_data.append(data['visibility'] * self.M_TO_MI)
					weather_data.append(data['wind_speed'])
					if ('rain' in data and '1h' in data['rain']):
						weather_data.append(data['rain']['1h'] * self.MM_TO_INCH)
					else:
						weather_data.append(0.009854445520487937)
					return weather_data

		return None