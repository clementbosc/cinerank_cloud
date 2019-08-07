# Import the database object (db) from the main application module
# We will define this inside /app/__init__.py in the next sections.
from database import Database
from models.tmdb_movie import TmdbMovie
from parser.rates.allocine_rate import AllocineRate
from parser.rates.imdb_rate import ImdbRate


class Movie:

	def __init__(self, id, tmdb_id, allocine_id, imdb_id):
		self.tmdb_id = tmdb_id
		self.id = id
		self.allocine_id = allocine_id
		self.imdb_id = imdb_id


	def update_rates(self):
		if not self.allocine_id or not self.imdb_id:
			self.tmdb_movie = TmdbMovie.get_film(self.tmdb_id)

		if self.allocine_id is None:
			self.allocine_id, _, _ = AllocineRate.call(self.tmdb_movie.original_title, self.tmdb_movie.title)

		if self.imdb_id is None:
			self.imdb_id = self.tmdb_movie.get_external_ids()['imdb_id']
			self.imdb_id = (None if self.imdb_id == '' or not self.imdb_id else self.imdb_id[2:])

		Database.execute("""UPDATE movies SET allocine_id = %s, imdb_id = %s where id=%s""", (self.allocine_id, self.imdb_id, self.id), 'none')
		allocine_rate, allocine_number_rate, imdb_rate, imdb_number_rate = None, None, None, None

		if self.allocine_id is not None:
			_, allocine_rate, allocine_number_rate = AllocineRate().get_rate(self.allocine_id)

		if self.imdb_id is not None:
			_, imdb_rate, imdb_number_rate = ImdbRate().get_rate(self.imdb_id)

		if allocine_rate is not None:
			Database.execute(
				"""INSERT INTO rates(rate, rate_number, site, movie_id) VALUES (%s, %s, %s, %s)""", (allocine_rate*2, allocine_number_rate, "allocine", self.id),
				'none')

		if imdb_rate is not None:
			Database.execute(
				"""INSERT INTO rates(rate, rate_number, site, movie_id) VALUES (%s, %s, %s, %s)""", (imdb_rate, imdb_number_rate, "imdb", self.id),
				'none')
