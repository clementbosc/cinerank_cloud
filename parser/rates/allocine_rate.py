import json
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
import unidecode

from bs4 import BeautifulSoup

from parser.rates.rate_parser import RateParser


def similar(a, b):
	# return unidecode.unidecode(a.strip().lower()) == unidecode.unidecode(b.strip().lower())
	return SequenceMatcher(None, unidecode.unidecode(a.strip().lower()), unidecode.unidecode(b.strip().lower())).ratio() > 0.8


class AllocineRate(RateParser):

	def __init__(self):
		super().__init__('http://www.allocine.fr/film/fichefilm_gen_cfilm=', suffix='.html')

	@staticmethod
	def call(original_name, local_name, year=None):
		trouve = False
		j = 0
		movie_link = None

		names = [original_name, local_name]

		while (not trouve) and j < len(names):
			allocine_query = names[j]
			search_link = 'http://www.allocine.fr/recherche/?q=' + urllib.parse.quote_plus(allocine_query)

			content = RateParser.open_link(search_link)
			page = BeautifulSoup(content, "html.parser")

			table = page.select('table.totalwidth.noborder.purehtml')
			if len(table) == 0:
				j += 1
				continue
			table = table[0]
			links = table.select('tr td.totalwidth a')

			i = 0

			if len(links) == 0:
				j += 1
				continue

			while (not trouve) and i < len(links):
				movie_name = links[i].text
				movie_link = links[i]['href']
				trouve = (similar(movie_name, original_name) or similar(movie_name, local_name))
				i += 1

			j += 1

		if movie_link is None:
			return None, None, None

		allocine_id = movie_link[26:][:-5]

		return AllocineRate().get_rate(allocine_id)

	def get_rate(self, allocine_id):
		return super().get_rate(allocine_id)
