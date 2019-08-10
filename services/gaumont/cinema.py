import json
from datetime import datetime

from dateutil.parser import parse
from pytz import timezone

from services.gaumont.file_manager import FileManager
from services.gaumont.seance import Seance


class Cinema:
	json_seances_day = {}  # cine_id => film_id => days
	json_seances = {}  # cine_id => film_id => days => showtimes
	json_cinemas = None



	def __init__(self, id, name, address, ville, lat, lng):
		self.id = id
		self.name = name
		self.address = address
		self.ville = ville
		self.lat = lat
		self.lng = lng
		self.seances_days = None  # film_id => days
		self.seances = {}  # film_id => days => showtimes
		self.films = None

	def toJSON(self):
		return json.dumps(self, default=lambda o: o.__dict__,
						  sort_keys=True, indent=4)

	def get_seances_days(self, film_id):
		if self.seances_days is not None and film_id in self.seances_days:
			return self.seances_days[film_id]

		if self.id not in Cinema.json_seances_day:
			Cinema.json_seances_day[self.id] = \
			FileManager.call("shows_" + self.id, "https://www.cinemaspathegaumont.com/api/cinema/" + self.id + "/shows",
							 172800)['shows']

		self.seances_days = {}

		for f in Cinema.json_seances_day[self.id]:
			self.seances_days[f] = set()
			for day in Cinema.json_seances_day[self.id][f]['days']:
				if Cinema.json_seances_day[self.id][f]['days'][day]['bookable']:
					self.seances_days[f].add(day)

		return self.seances_days[film_id]

	def get_seances_by_day(self, film_id, day):
		if self.seances is not None and film_id in self.seances and day in self.seances[film_id]:
			return self.seances[film_id][day]

		if self.id not in self.seances:
			self.seances[self.id] = {}

		if film_id not in self.seances[self.id]:
			self.seances[self.id][film_id] = {}

		self.seances[self.id][film_id][day] = FileManager.call("showtimes_" + self.id + '_' + film_id + '_' + day,
															   "https://www.cinemaspathegaumont.com/api/show/" + film_id + "/showtimes/" + self.id + "/" + day,
															   172800)

		return self.seances[self.id][film_id][day]

	def get_all_seances(self, film_id):
		seances = []
		for day in self.get_seances_days(film_id):
			seances = seances + self.get_seances_by_day(film_id, day)

		return seances

	def get_films(self, sortis=True):
		if self.films is not None:
			return self.films

		if self.id not in Cinema.json_seances_day:
			Cinema.json_seances_day[self.id] = \
			FileManager.call("shows_" + self.id, "https://www.cinemaspathegaumont.com/api/cinema/" + self.id + "/shows",
							 172800)["shows"]

		self.films = []

		present = datetime.now(timezone('UTC'))
		from services.gaumont.film_gaumont import FilmGaumont
		for film_id in Cinema.json_seances_day[self.id]:
			film = FilmGaumont.get_film(film_id)
			if film not in self.films and film is not None:
				if sortis:
					if film.sortie.date() < present.date():
						self.films.append(film)
				else:
					self.films.append(film)

		return self.films

	@staticmethod
	def get_cinemas():
		if Cinema.json_cinemas is not None:
			return Cinema.json_cinemas

		json_cinemas = FileManager.call("cinemas", "https://www.cinemaspathegaumont.com/api/cinemas")
		Cinema.json_cinemas = []

		for c in json_cinemas:
			cine = Cinema(c['slug'], c['name'], c['theaters'][0]['addressLine1'], c['theaters'][0]['addressCity'],
						  c['theaters'][0]['gpsPosition']['x'], c['theaters'][0]['gpsPosition']['x'])
			Cinema.json_cinemas.append(cine)

		return Cinema.json_cinemas

	@staticmethod
	def get_cinema(cine_id):
		cinemas = Cinema.get_cinemas()
		for c in cinemas:
			if c.id == cine_id:
				return c
		return None

	def __str__(self):
		return str(self.id) + '\t' + self.name

	def get_upcoming_seances(self):
		seances = self.get_seances()
		present = datetime.now(timezone('UTC'))
		return [s for s in seances if s.timestamp > present]

	def get_today_upcoming_seances(self):
		seances = self.get_seances()
		present = datetime.now(timezone('UTC'))
		return [s for s in seances if s.timestamp > present and s.timestamp.date() == present.date()]


if __name__ == '__main__':
	for c in Cinema.get_cinemas():
		print(c.name)
		print('\t' + str([m.name for m in c.get_films()]))
