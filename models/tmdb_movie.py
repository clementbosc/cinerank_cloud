import json
import ssl
import urllib.error
import urllib.parse
import urllib.parse
import urllib.request

from dateutil.parser import parse

from models import tmdb_language, tmdb_api_key


def simple_production_countries(production_countries):
	return map(lambda x: x['iso_3166_1'], production_countries)


class TmdbMovie:
	def __init__(self, **kwargs):
		# super(TmdbMovie, self).__init__(**kwargs)
		self.release_dates = None
		self.external_ids = None
		self.people = None
		self.videos = None
		self.id = kwargs.get("id")
		self.backdrop_path = kwargs.get("backdrop_path")
		self.original_language = kwargs.get("original_language")
		self.original_title = kwargs.get("original_title")
		self.overview = kwargs.get("overview")
		self.poster_path = kwargs.get("poster_path")
		self.release_date = kwargs.get("release_date")
		self.title = kwargs.get("title")

	def get_poster_path(self):
		if self.poster_path is None:
			return None
		return 'https://image.tmdb.org/t/p/w500' + self.poster_path

	def get_backdrop_path(self):
		if self.backdrop_path is None:
			return None
		return 'https://image.tmdb.org/t/p/original' + self.backdrop_path

	@staticmethod
	def get_now_playing(page=1):

		now_playing_movies = []

		content_url = 'https://api.themoviedb.org/3/movie/now_playing?api_key=' + tmdb_api_key + \
					  '&language=' + tmdb_language + '&page=' + str(page) + '&region=FR'

		ssl._create_default_https_context = ssl._create_unverified_context
		with urllib.request.urlopen(content_url) as url:
			results = json.loads(url.read().decode())['results']

			for res in results:
				tmdb_movie = TmdbMovie(id=res['id'],
									   original_title=res['original_title'],
									   poster_path=res['poster_path'],
									   backdrop_path=res['backdrop_path'],
									   title=res['title'],
									   overview=res['overview'],
									   original_language=res['original_language'])
				now_playing_movies.append(tmdb_movie)
				# db.session.add(tmdb_movie)
		# db.session.commit()

		return now_playing_movies

	@staticmethod
	def search_in_now_playing(tmdb_id, nb_pages=1):

		for page in range(nb_pages):
			page = page + 1

			for tmdb_movie in TmdbMovie.get_now_playing(page):
				if tmdb_movie.id == tmdb_id:
					return tmdb_movie

		return None

	@staticmethod
	def all_now_playing(nb_pages=1):

		for page in range(nb_pages):
			page = page + 1

			for tmdb_movie in TmdbMovie.get_now_playing(page):
				yield tmdb_movie

	@staticmethod
	def get_film(movie_id):

		content_url = 'https://api.themoviedb.org/3/movie/' + str(movie_id) + \
					  '?api_key=' + tmdb_api_key + '&language=' + tmdb_language

		ssl._create_default_https_context = ssl._create_unverified_context
		try:
			with urllib.request.urlopen(content_url) as url:
				res = json.loads(url.read().decode())
				movie = TmdbMovie(id=res['id'],
								  original_title=res['original_title'],
								  poster_path=res['poster_path'],
								  backdrop_path=res['backdrop_path'],
								  title=res['title'],
								  overview=res['overview'],
								  original_language=res['original_language'])

				return movie
		except urllib.error.HTTPError as e:
			return None



	@staticmethod
	def search_film(movie_name, year):

		content_url = 'https://api.themoviedb.org/3/search/multi?query=' + urllib.parse.quote_plus(movie_name) + \
					  '&api_key=' + tmdb_api_key + '&include_adult=false&language=' + tmdb_language + '&year=' + str(
			year)

		print(content_url)

		ssl._create_default_https_context = ssl._create_unverified_context
		with urllib.request.urlopen(content_url) as url:
			results = json.loads(url.read().decode())['results']
			for res in results:
				release_date = parse(res['release_date']) if 'release_date' in res and res['release_date'] != '' else None
				if res['media_type'] == 'movie' and release_date is not None and (year - 1 < release_date.year < year + 1):
					return TmdbMovie(id=int(res['id']),
									 original_title=res['original_title'],
									 poster_path=res['poster_path'],
									 backdrop_path=res['backdrop_path'],
									 title=res['title'],
									 overview=res['overview'],
									 original_language=res['original_language'])




	def get_external_ids(self):
		if self.external_ids is not None:
			return self.external_ids

		content_url = "https://api.themoviedb.org/3/movie/" + str(self.id) + "/external_ids?api_key=" + tmdb_api_key
		with urllib.request.urlopen(content_url) as url:
			self.external_ids = json.loads(url.read().decode())
			return self.external_ids

	def get_release_dates(self):
		if self.release_dates is not None:
			return self.release_dates

		content_url = "https://api.themoviedb.org/3/movie/" + str(self.id) + "/release_dates?api_key=" + tmdb_api_key
		with urllib.request.urlopen(content_url) as url:
			self.release_dates = json.loads(url.read().decode())
			return self.release_dates

	def french_release_date(self):
		for date in self.get_release_dates()['results']:
			if date['iso_3166_1'] == 'FR':
				return parse(date['release_dates'][0]['release_date'])
		return None

