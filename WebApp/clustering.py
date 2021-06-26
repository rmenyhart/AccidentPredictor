from dtos.location import Location
from sklearn.metrics.pairwise import haversine_distances
from math import radians

class Clustering:
	cluster_centers = []

	def load_centers(self, filename):
		file = open(filename, 'r')
		for line in file:
			coords = line.split(',')
			self.cluster_centers.append(Location(float(coords[0]), float(coords[1])))

	def is_clustered(self, point, distance):
		for center in self.cluster_centers:
			if (self.haversine(point, center) <= distance):
				return True
		return False

	def haversine(self, loc1, loc2):
		loc1_rad = [radians(loc1.lat), radians(loc1.lng)]
		loc2_rad = [radians(loc2.lat), radians(loc2.lng)]
		result = haversine_distances([loc1_rad, loc2_rad])
		return result[0][1]


