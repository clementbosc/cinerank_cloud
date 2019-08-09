from database import Database
from models.movie import Movie
from models.tmdb_movie import TmdbMovie
from parser.gaumont_parser import GaumontParser


# from psycopg2 import OperationalError
from services.gaumont.cinema import Cinema


class CronJobs:

	@staticmethod
	def parse_gaumont_movies():
		processed_gaumont_films = []
		for c in Cinema.get_cinemas():
			for film in c.get_films():
				if film.id in processed_gaumont_films:
					continue
				processed_gaumont_films.append(film.id)
				# si on a pas déjà l'id dans la DB
				if Database.execute("""SELECT count(*) FROM movies where gaumont_id=%s""", (film.id,), 'one')[0] == 0:
					tmdb_movie = TmdbMovie.search_film(film.name, film.sortie.year)
					if tmdb_movie is None:
						continue
					tmdb_id = tmdb_movie.id
					# si on a déjà le film mais pas lié à l'id gaumont
					if Database.execute("""SELECT count(*) FROM movies where tmdb_id=%s""", (tmdb_id,), 'one')[0] > 0:
						movie_id, allocine_id, imdb_id = Database.execute(
							"""UPDATE movies SET gaumont_id = %s, to_display = TRUE WHERE tmdb_id=%s RETURNING id, allocine_id, imdb_id""",
							(film.id, tmdb_id), 'one')
					else:
						# si on a pas le film
						movie_id, allocine_id, imdb_id = Database.execute(
							"""INSERT INTO MOVIES(gaumont_id, tmdb_id, release_date, to_display, name, backdrop_path, poster_path) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, allocine_id, imdb_id""",
							(film.id, tmdb_id, tmdb_movie.french_release_date(), True, tmdb_movie.title,
							 tmdb_movie.backdrop_path, tmdb_movie.poster_path),
							'one')
				else:
					movie_id, tmdb_id, allocine_id, imdb_id = Database.execute(
						"""UPDATE movies SET to_display = TRUE WHERE gaumont_id = %s RETURNING id, tmdb_id, allocine_id, imdb_id""",
						(film.id,), 'one')

				movie = Movie(movie_id, tmdb_id, allocine_id, imdb_id)
				movie.update_rates()

		Database.execute(
			"""UPDATE movies SET to_display = FALSE WHERE gaumont_id NOT IN %s""",
			(tuple(processed_gaumont_films),), 'none')


if __name__ == '__main__':
	CronJobs.parse_gaumont_movies()
