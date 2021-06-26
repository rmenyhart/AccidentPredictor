from flask import Flask, render_template, send_file, request, redirect, jsonify, flash
import json
import requests
from location import Location
from map import Map
from clustering import Clustering
from datetime import datetime, timedelta, timezone
from pytz import UTC as utc

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
GMAPS_API_KEY="AIzaSyBCyCMKoSaUd7fuXmpPceSRxV0yYEc7u-o"
WEATHER_API_KEY="1bfdf37c545388842d5215319e0d7c56"
maps = []
hotspots = []

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/doc')
def download():
	return send_file('doc/doc.txt', as_attachment=True)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
	if request.method == 'POST':
		origin_text = request.form['from']
		dest_text = request.form['to']
		date = request.form['date']
		time = request.form['time']
		origin_lat = 0.0
		origin_lng = 0.0
		dest_lat = 0.0
		dest_lng = 0.0

		#Check correctness of datetime
		current_time_local = datetime.now().replace(second=0, microsecond = 0)
		current_time_utc = datetime.utcnow().replace(second=0, microsecond = 0, tzinfo=timezone.utc)
		selected_time_local = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M').replace(second=0, microsecond=0)
		utc_offset = datetime.now() - datetime.utcnow()
		selected_time_utc = selected_time_local - utc_offset
		selected_time_utc = selected_time_utc.replace(tzinfo=timezone.utc)
		if (selected_time_utc - current_time_utc > timedelta(hours=48)):
			return 'Please select a time from the next 48 hours for forecasting'
		elif (current_time_utc - selected_time_utc > timedelta(days=5)):
			return 'Please select a time from the previous 5 days for historical weather data'

		#Get origin coordinates
		base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
		params = {
			'key': GMAPS_API_KEY,
			'address': origin_text
		}
		response = requests.get(base_url, params=params).json()
		if (response['status'] == 'OK'):
			origin_lat = float(json.dumps(response['results'][0]['geometry']['location']['lat']))
			origin_lng = float(json.dumps(response['results'][0]['geometry']['location']['lng']))
		else:
			return 'Error finding origin point.'

		#Get destination coordinates
		base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
		params = {
			'key': GMAPS_API_KEY,
			'address': dest_text
		}
		response = requests.get(base_url, params=params).json()
		if (response['status'] == 'OK'):
			dest_lat = float(json.dumps(response['results'][0]['geometry']['location']['lat']))
			dest_lng = float(json.dumps(response['results'][0]['geometry']['location']['lng']))
		else:
			return 'Error finding destination point.'

		#Get route coordinates
		waypoints = []
		base_url = 'https://maps.googleapis.com/maps/api/directions/json?'
		params = {
			'origin': str(origin_lat) + str(',') + str(origin_lng),
			'destination': str(dest_lat) + str(',') + str(dest_lng),
			'key': GMAPS_API_KEY
		}
		response = requests.get(base_url, params=params).json()
		if (response['status'] == 'OK'):
			is_first = True;
			for leg in response['routes'][0]['legs']:
				for step in leg['steps']:
					if (is_first):
						waypoints.append(Location(step['start_location']['lat'], step['start_location']['lng']))
						is_first = False
					waypoints.append(Location(step['end_location']['lat'], step['end_location']['lng']))
			hotspots.append(waypoints)
		else:
			return 'Error getting waypoints.'

		#Get weather data
		if selected_time_utc < current_time_utc:
			#Get historical data
			base_url = 'https://api.openweathermap.org/data/2.5/onecall/timemachine?'
			params = {
				'lat': origin_lat,
				'lon': origin_lng,
				'dt': selected_time_utc.strftime('%s'),
				'appid': WEATHER_API_KEY
			}
			response = requests.get(base_url, params=params).json()
			return json.dumps(response)
		elif selected_time_utc == current_time_utc:
			#Get current weather
			base_url = 'https://api.openweathermap.org/data/2.5/onecall?'
			params = {
				'lat': origin_lat,
				'lon': origin_lng,
				'exclude': 'minutely,hourly,daily,alerts',
				'appid': WEATHER_API_KEY
			}
			response = requests.get(base_url, params=params).json()
			return json.dumps(response)
		else:
			#Get forecast
			base_url = 'https://api.openweathermap.org/data/2.5/onecall?'
			params = {
				'lat': origin_lat,
				'lon': origin_lng,
				'exclude': 'current,minutely,daily,alerts',
				'appid': WEATHER_API_KEY
			}
			response = requests.get(base_url, params=params).json()
			return json.dumps(response)

		n_maps = len(maps)
		origin = Location(origin_lat, origin_lng)
		destination = Location(dest_lat, dest_lng)
		mymap = Map(origin, destination, n_maps)
		maps.append(mymap)
		return redirect('/' + str(n_maps))

@app.route('/<map_code>')
def show_map(map_code):
	last_map = maps[int(map_code)]
	last_hotspots = hotspots[int(map_code)]
	return render_template('map.html', map = last_map, API_KEY = GMAPS_API_KEY, hotspots=last_hotspots)

@app.route('/waypoints/<wp_code>')
def waypoints(wp_code):
	last_waypoints = hotspots[int(wp_code)]
	detailed_waypoints = []
	for wp in last_waypoints:
		wp_details = {
			'lat': wp.lat,
			'lng': wp.lng
		}
		detailed_waypoints.append(wp_details)
	return jsonify({'waypoints': detailed_waypoints})


if __name__ == '__main__':
	clustering = Clustering()
	clustering.load_centers('cluster_centers.csv')
	app.run(debug=True)