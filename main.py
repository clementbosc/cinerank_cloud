import json
from datetime import datetime
from pytz import timezone

from flask import Flask

from cron_jobs import CronJobs
from database import Database
from services.gaumont.cinema import Cinema
from services.gaumont.film_gaumont import FilmGaumont
from dateutil.parser import parse as parse_date

app = Flask(__name__)


@app.route('/parse')
def parse():
	print(CronJobs.parse_gaumont_movies())
	return 'f'


@app.route('/rates')
def get_rates():
	movies = Database.execute(
		"""SELECT name, gaumont_id, imdb_id, allocine_id, tmdb_id, backdrop_path, poster_path, score::float, rates
		FROM ranked_movies;""", (), 'all')
	return json.dumps({'movies': [{
		'name': x[0],
		'gaumont_id': x[1],
		'imdb_id': x[2],
		'allocine_id': x[3],
		'tmdb_id': x[4],
		'backdrop_path': x[5],
		'poster_path': x[6],
		'score': x[7],
		'rates': {s: float(r) for s, r in x[8].items()}} for x in movies]})


@app.route('/cinemas/<string:slug>/rates')
def cinemas_rates(slug):
	slugs = [m.id for m in Cinema.get_cinema(slug).get_films()]
	movies = Database.execute(
		"""SELECT name, gaumont_id, imdb_id, allocine_id, tmdb_id, backdrop_path, poster_path, score::float, rates
		FROM ranked_movies WHERE gaumont_id IN %s;""", (tuple(slugs),), 'all')
	return json.dumps({'movies': [{
		'name': x[0],
		'gaumont_id': x[1],
		'imdb_id': x[2],
		'allocine_id': x[3],
		'tmdb_id': x[4],
		'backdrop_path': x[5],
		'poster_path': x[6],
		'score': x[7],
		'rates': {s: float(r) for s, r in x[8].items()}} for x in movies]})


@app.route('/cinemas/<string:slug>/movies/<string:gaumont_id>/showtimes')
def cinema_movie_showtimes(slug, gaumont_id):
	movie = FilmGaumont.get_film(gaumont_id)
	return json.dumps(list(filter(
		lambda x: parse_date(x['reservabilityEnd']) > datetime.now(timezone('UTC')) and x['status'] == 'available',
		movie.get_seances(slug))))


@app.route('/cinemas/<string:slug>')
def get_cinema(slug):
	cinema = Cinema.get_cinema(slug)
	return {
		'id': cinema.id,
		'name': cinema.name,
		'address': cinema.address,
		'ville': cinema.ville,
		'lat': cinema.lat,
		'lng': cinema.lng
	}


@app.route('/cinemas')
def get_cinemas():
	return json.dumps([{
		'id': c.id,
		'name': c.name,
		'ville': c.ville
	} for c in Cinema.get_cinemas()])


if __name__ == '__main__':
	app.run()
