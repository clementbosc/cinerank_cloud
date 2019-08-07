import os
from os import getenv
import psycopg2.pool

import psycopg2


class Database:
	__db = None
	__pg_pool = None
	CONNECTION_NAME = getenv(
		'INSTANCE_CONNECTION_NAME',
		'cinerank-cloud:europe-west1:cinerank-postgres')
	DB_USER = getenv('POSTGRES_USER', 'postgres')
	DB_PASSWORD = getenv('POSTGRES_PASSWORD', 'NRpXLuziBVC3rbL')
	DB_NAME = getenv('POSTGRES_DATABASE', 'cinerank')

	pg_config = {
		'user': DB_USER,
		'password': DB_PASSWORD,
		'dbname': DB_NAME
	}

	@staticmethod
	def get_instance():
		if not Database.__db:
			# When deployed to App Engine, the `GAE_ENV` environment variable will be
			# set to `standard`
			if os.environ.get('GAE_ENV') == 'standard':
				# If deployed, use the local socket interface for accessing Cloud SQL
				host = '/cloudsql/{}'.format(Database.CONNECTION_NAME)
			else:
				# If running locally, use the TCP connections instead
				# Set up Cloud SQL Proxy (cloud.google.com/sql/docs/mysql/sql-proxy)
				# so that your application can use 127.0.0.1:3306 to connect to your
				# Cloud SQL instance
				host = '127.0.0.1'
			Database.__db = Database.__connect(host)
		return Database.__db

	@staticmethod
	def execute(query: str, args: tuple, fetchtype: str):
		cnx = Database.get_instance().getconn()
		result = None
		with cnx.cursor() as cursor:
			cursor.execute(query, args)
			if fetchtype == 'all':
				result = cursor.fetchall()
			elif fetchtype == 'one':
				result = cursor.fetchone()
			else:
				result = None
		cnx.commit()
		Database.get_instance().putconn(cnx)
		return result

	@staticmethod
	def __connect(host):
		"""
		Helper function to connect to Postgres
		"""
		Database.pg_config['host'] = host
		return psycopg2.pool.ThreadedConnectionPool(minconn=1, maxconn=3, **Database.pg_config)
