import datetime
import ssl
from difflib import SequenceMatcher

import requests
from dateutil.parser import parse

from services.gaumont.film_gaumont import FilmGaumont


def similar(a, b):
	return SequenceMatcher(None, a, b).ratio() > 0.8


class GaumontParser:
	show_url = 'https://www.cinemaspathegaumont.com/api/shows'
	cine_url = 'https://www.cinemaspathegaumont.com/api/cinema/cinema-gaumont-wilson/shows'

	def __init__(self):
		self.slugs = {}
		self.wilson_shows = None
		self.release_dates = {}

	def get_slug(self, normal_name):
		for s in self.get_all_slugs():
			if similar(normal_name, s):
				return self.get_all_slugs()[s]
		return None

	def get_movie_name(self, slug):
		my_inverted_dict = {value: key for key, value in self.get_all_slugs().items()}
		if slug not in my_inverted_dict:
			return None
		return my_inverted_dict[slug]

	def get_all_slugs(self):
		if len(self.slugs) == 0:
			ssl._create_default_https_context = ssl._create_unverified_context
			r = requests.get(GaumontParser.show_url, headers={'user-agent': 'cinerank'})
			for s in r.json()['shows']:
				self.release_dates[s['slug']] = parse(s['releaseAt'])
				self.slugs[s['title'].replace('La soirée des passionnés ', '')] = s['slug']

		return self.slugs

	def load_wilson_shows(self):
		if self.wilson_shows is None:
			ssl._create_default_https_context = ssl._create_unverified_context
			r = requests.get(GaumontParser.cine_url, headers={'user-agent': 'cinerank'})
			self.wilson_shows = r.json()['shows']

	def is_playing(self, movie_name):
		slug = self.get_slug(movie_name)
		if slug is None:
			return False

		self.load_wilson_shows()

		if slug not in self.wilson_shows:
			return False

		playing_days = set(self.wilson_shows[slug]['days'].keys())
		next_days = [datetime.datetime.today() + datetime.timedelta(days=x) for x in range(0, 7)]
		next_days = set([x.strftime('%Y-%m-%d') for x in next_days])

		return self.wilson_shows[slug]['isBookable'] and len(next_days & playing_days) > 0

	def now_playing_shows(self):

		now_playing = []

		self.load_wilson_shows()

		next_days = [datetime.datetime.today() + datetime.timedelta(days=x) for x in range(0, 7)]
		next_days = set([x.strftime('%Y-%m-%d') for x in next_days])

		for slug in self.wilson_shows:
			playing_days = set(self.wilson_shows[slug]['days'].keys())
			if self.wilson_shows[slug]['isBookable'] and len(next_days & playing_days) > 0:
				if self.get_movie_name(slug) is not None:
					now_playing.append(FilmGaumont(slug, self.get_movie_name(slug).lower().replace('il était une fois...', ''), '', self.release_dates[slug]))

		return now_playing


if __name__ == '__main__':
	p = GaumontParser()
	p.load_wilson_shows()
	print(p.wilson_shows)
	print([p.get_movie_name(f.id) for f in p.now_playing_shows()])
	#print(p.get_slug('Creed 2'))
	#slug = p.get_slug('Creed 2')
	#print(p.get_movie_name(slug))
	#print(p.is_playing(slug))
#
