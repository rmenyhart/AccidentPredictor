from dtos.location import Location
import requests

class GmapsService:
	API_KEY = ''
	geocoding_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
	directions_url = 'https://maps.googleapis.com/maps/api/directions/json?'

	def __init__(self, API_KEY):
		self.API_KEY = API_KEY

	def getCoordinatesByAddress(self, address):
		params = {
			'key': self.API_KEY,
			'address': address
		}
		response = requests.get(self.geocoding_url, params=params).json()
		if (response['status'] == 'OK'):
			lat = response['results'][0]['geometry']['location']['lat']
			lng = response['results'][0]['geometry']['location']['lng']
			return Location(lat, lng)
		return None

	def getRouteCoordinates(self, origin, destination):
		waypoints = []
		params = {
			'origin': str(origin.lat) + str(',') + str(origin.lng),
			'destination': str(destination.lat) + str(',') + str(destination.lng),
			'key': self.API_KEY
		}
		response = requests.get(self.directions_url, params=params).json()
		if (response['status'] == 'OK'):
			is_first = True;
			for leg in response['routes'][0]['legs']:
				for step in leg['steps'][:-1]:
					waypoints.append(Location(step['end_location']['lat'], step['end_location']['lng']))
			return waypoints
		return None