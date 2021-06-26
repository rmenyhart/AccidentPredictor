from dtos.location import Location
class Map:
	map_id = 0
	origin = Location(0, 0)
	destination = Location(0, 0)

	def __init__(self, origin, destination, map_id):
		self.origin = origin
		self.destination = destination
		self.map_id = map_id