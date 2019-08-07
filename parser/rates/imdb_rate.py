from parser.rates.rate_parser import RateParser


class ImdbRate(RateParser):

	def __init__(self):
		super().__init__("https://www.imdb.com/title/tt")

	@staticmethod
	def call(imdb_id):
		if imdb_id[:2] == 'tt':
			imdb_id = imdb_id[2:]

		return ImdbRate().get_rate(imdb_id)

	def get_rate(self, imdb_id):
		return super().get_rate(str(imdb_id).zfill(7))
