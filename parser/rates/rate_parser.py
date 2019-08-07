import re
import ssl

from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
import urllib.error


class RateParser:

	def __init__(self, base_url, suffix=None):
		self.base_url = base_url
		self.suffix = suffix

	@staticmethod
	def open_link(link):
		try:
			ssl._create_default_https_context = ssl._create_unverified_context
			with urllib.request.urlopen(link) as url:
				return url.read()
		except urllib.error.HTTPError as e:
			return None

	def get_rate(self, id):

		if id is None:
			return None, None, None

		try:
			link = self.base_url + str(id) + (self.suffix if self.suffix is not None else '')
			page = BeautifulSoup(RateParser.open_link(link), "html.parser")
			script_text = page.find('script', type='application/ld+json')

			if script_text is None:
				return id, None, None

			script_text = script_text.text

			regex = r"\"aggregateRating\": ?{[ \n]*(?:(?:\"ratingValue\": ?\"(?P<ratingValue>[0-9,.]+)\")|(?:\"@type\": ?\"AggregateRating\")|[, \n]*|(?:\"bestRating\": ?\"(?P<bestRating>[0-9,.]+)\")|(?:\"worstRating\": ?\"(?P<worstRating>[0-9,.]+)\")|(?:\"reviewCount\": ?\"(?P<reviewCount>[0-9,.]+)\")|(?:\"ratingCount\": ?(?:\")?(?P<ratingCount>[0-9]+)(?:\")?))+[ \n]*?}"

			m = re.search(regex, script_text, re.MULTILINE | re.DOTALL)

			if m is None:
				return id, None, None

			values = m.groupdict()

			return id, float(values['ratingValue'].replace(',', '.')), int(values['ratingCount'])

		except urllib.error.HTTPError:
			return id, None, None
