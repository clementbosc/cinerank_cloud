# -*- coding: utf-8 -*-
import io
import json
import os
import re
import ssl
import time
import urllib.request

import requests

from google.cloud import storage


def file_timestamp(name, file_name):
	return file_name[len(name) + 1::][:-5]


def load_json(content_url):
	ssl._create_default_https_context = ssl._create_unverified_context
	with urllib.request.urlopen(content_url) as url:
		return json.loads(url.read().decode())


class FileManager:
	instance = None

	def __init__(self):
		client = storage.Client()
		self.bucket = client.get_bucket('cinerank-cloud.appspot.com')

	@staticmethod
	def call(name, url, delay=604800):
		if FileManager.instance is None:
			FileManager.instance = FileManager()

		file_exists, timestamp, blob = FileManager.instance.file_exists(name)
		filename = name + "_" + str(int(time.time())) + ".json"
		if not file_exists or int(time.time()) > (
				int(timestamp) + delay):  # si le fichier n'existe pas ou date de plus d'une semaine
			if file_exists and int(time.time()) > (int(timestamp) + delay):
				blob.delete()
			content = FileManager.instance.create_file(url, filename)
			return content
		else:
			return FileManager.instance.get_file_content(blob)

	def file_exists(self, name):
		regex = re.compile('(^' + name + '_[0-9]+\.json$)')

		for blob in self.bucket.list_blobs(prefix="json_files/"):
			if regex.match(blob.name.replace('json_files/', '')):
				return True, file_timestamp(name, blob.name.replace('json_files/', '')), blob
		return False, 0, None

	def create_file(self, url, filename):
		headers = {'user-agent': 'cinerank'}
		r = requests.get(url, headers=headers)
		content = r.content

		blob = self.bucket.blob('json_files/' + filename)
		blob.upload_from_string(content)

		return r.json()

	def get_file_content(self, blob):
		print('get_file_content')
		return json.loads(blob.download_as_string().decode('utf-8'))
