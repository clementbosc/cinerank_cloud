from datetime import datetime

from dateutil.parser import parse
from pytz import timezone

from services.gaumont.file_manager import FileManager
from services.gaumont.seance import Seance


class Cinema:
    json_seances = {}
    json_cinemas = None

    def __init__(self, id, name, address, ville, lat, lng):
        self.id = id
        self.name = name
        self.address = address
        self.ville = ville
        self.lat = lat
        self.lng = lng
        self.seances = None
        self.films = None

    def get_seances(self, film_id=None):
        if self.seances is not None:
            if film_id is not None:
                return [x for x in self.seances if x.film_id == film_id]
            else:
                return self.seances

        if self.zone not in Cinema.json_seances:
            Cinema.json_seances[self.zone] = FileManager.call("seances_"+str(self.zone), "https://api.cinemasgaumontpathe.com/seance/1/zone/"+str(self.zone), 172800)['seances'] #load_json("https://api.cinemasgaumontpathe.com/seance/1/zone/"+str(self.zone))['seances']

        self.seances = []

        for f in Cinema.json_seances[self.zone]:
            if f['c'] == self.id:
                for s in f['hor']:
                    if 'd' in s:
                        seance = Seance(s['id'], parse(s['d']), f['f'], s['sp'], f['v'])
                        self.seances.append(seance)

        if film_id is not None:
            return [x for x in self.seances if x.film_id == film_id]

        return self.seances

    def get_films(self, sortis=True):
        if self.films is not None:
            return self.films

        if self.id not in Cinema.json_seances:
            Cinema.json_seances[self.id] = FileManager.call("shows_"+str(self.id), "https://www.cinemaspathegaumont.com/api/cinema/"+str(self.id)+"/shows", 172800)["shows"]

        self.films = []

        present = datetime.now(timezone('UTC'))
        from services.gaumont.film_gaumont import FilmGaumont
        for film_id in Cinema.json_seances[self.id]:
            film = FilmGaumont.get_film(film_id)
            if film not in self.films and film is not None:
                if sortis:
                    if film.sortie.date() < present.date():
                        self.films.append(film)
                else:
                    self.films.append(film)

        return self.films

    @staticmethod
    def get_cinemas():
        if Cinema.json_cinemas is not None:
            return Cinema.json_cinemas

        json_cinemas = FileManager.call("cinemas", "https://www.cinemaspathegaumont.com/api/cinemas")
        Cinema.json_cinemas = []

        for c in json_cinemas:
            cine = Cinema(c['slug'], c['name'], c['theaters'][0]['addressLine1'], c['theaters'][0]['addressCity'], c['theaters'][0]['gpsPosition']['x'], c['theaters'][0]['gpsPosition']['x'])
            Cinema.json_cinemas.append(cine)

        return Cinema.json_cinemas

    @staticmethod
    def get_cinema(cine_id):
        cinemas = Cinema.get_cinemas()
        for c in cinemas:
            if c.id == cine_id:
                return c
        return None

    def __str__(self):
        return str(self.id)+'\t'+self.name

    def get_upcoming_seances(self):
        seances = self.get_seances()
        present = datetime.now(timezone('UTC'))
        return [s for s in seances if s.timestamp > present]

    def get_today_upcoming_seances(self):
        seances = self.get_seances()
        present = datetime.now(timezone('UTC'))
        return [s for s in seances if s.timestamp > present and s.timestamp.date() == present.date()]



if __name__ == '__main__':
    for c in Cinema.get_cinemas():
        print(c.name)
        print('\t'+str([m.name for m in c.get_films()]))
