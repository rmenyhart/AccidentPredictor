from flask import Flask, render_template, send_file, request, redirect, jsonify, flash
from dtos.location import Location
from dtos.map import Map
from clustering import Clustering
from classifier import Classifier
from datetime import datetime, timedelta, timezone
from services.gmaps import GmapsService
from services.openweather import OpenWeatherService
import math
import sys

app = Flask(__name__)

GMAPS_API_KEY="removed"
gmaps = GmapsService(GMAPS_API_KEY)

OPENW_API_KEY="removed"
openw = OpenWeatherService(OPENW_API_KEY)

maps = []
hotspots = []

clustering = Clustering()
clustering.load_centers('cluster_centers.csv')

classifier = Classifier()
classifier.load_classifier('model.sav')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/doc')
def download():
	return send_file('doc/doc.txt', as_attachment=True)

@app.route('/predict', methods=['GET', 'POST'])
def predict():
	if request.method == 'POST':
		origin_address = request.form['from']
		dest_address = request.form['to']
		date = request.form['date']
		time = request.form['time']

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

		print('Time correct', file=sys.stderr)
		#Get origin coordinates
		origin = gmaps.getCoordinatesByAddress(origin_address)
		if (origin == None):
			return 'Error finding origin point.'

		#Get destination coordinates
		destination = gmaps.getCoordinatesByAddress(dest_address)
		if (destination == None):
			return 'Error finding destination point.'

		print('Found orig and dest', file=sys.stderr)

		#Get route coordinates
		waypoints = gmaps.getRouteCoordinates(origin, destination)
		if (waypoints == None):
			return 'Error getting waypoints.'

		print('Found route', file=sys.stderr)

		#Filter the clustered waypoints
		clustered_waypoints = []
		for wp in waypoints:
			if clustering.is_clustered(wp, 0.03):
				clustered_waypoints.append(wp)

		print('Found clustered', file=sys.stderr)

		#Filter active clustered waypoints
		active_clustered_waypoints = []
		for wp in clustered_waypoints:
			weather_data = openw.getWeather(wp, selected_time_utc, current_time_utc)
			if (weather_data != None):
				data = []
				data.extend([wp.lat, wp.lng])
				data.extend(weather_data)
				data.extend([selected_time_local.month, selected_time_local.weekday(), selected_time_local.hour, selected_time_local.minute])
				pred = classifier.predict([data])[0]
				print(data, file=sys.stderr)
				print(pred, file=sys.stderr)
				if pred == 1:
					active_clustered_waypoints.append(wp)
			else:
				return 'Error getting weather data for (' + str(wp.lat) + ' , ' + str(wp.lng) + ')'

		print('Found active', file=sys.stderr)
		n_maps = len(maps)
		mymap = Map(origin, destination, n_maps)
		maps.append(mymap)
		hotspots.append(active_clustered_waypoints)
		return redirect('/map/' + str(n_maps))

@app.route('/map/<n_maps>')
def show_map(n_maps):
	last_map = maps[int(n_maps) - 1]
	last_hotspots = hotspots[int(n_maps) - 1]
	return render_template('map.html', map = last_map, API_KEY = GMAPS_API_KEY, hotspots=last_hotspots)

@app.route('/waypoints/<n_maps>')
def waypoints(n_maps):
	last_waypoints = hotspots[int(n_maps) - 1]
	detailed_waypoints = []
	for wp in last_waypoints:
		wp_details = {
			'lat': wp.lat,
			'lng': wp.lng
		}
		detailed_waypoints.append(wp_details)
	return jsonify({'waypoints': detailed_waypoints})


if __name__ == '__main__':
	app.run()
