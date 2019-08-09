from datetime import datetime

from dateutil.parser import parse
from pytz import timezone
from tzlocal import get_localzone

from services.gaumont.cinema import Cinema
from services.gaumont.file_manager import FileManager


class FilmGaumont:

    json_films = None

    def __init__(self, id:str, name, affiche, sortie):
        self.id = id
        self.name = name
        self.affiche = affiche
        self.sortie = sortie
        self.seances = {}

    def get_seances(self, cine_id):
        if cine_id in self.seances:
            return self.seances[cine_id]

        cine = Cinema.get_cinema(cine_id)
        self.seances[cine_id] = cine.get_all_seances(self.id)
        return self.seances[cine_id]

    @staticmethod
    def get_films():
        if FilmGaumont.json_films is not None:
            return FilmGaumont.json_films

        json_films = FileManager.call("shows", "https://www.cinemaspathegaumont.com/api/shows")['shows']
        FilmGaumont.json_films = []

        for f in json_films:
            film = FilmGaumont(f['slug'], f['title'], None, parse(f['releaseAt']))
            FilmGaumont.json_films.append(film)

        return FilmGaumont.json_films

    @staticmethod
    def get_film(film_id):
        films = FilmGaumont.get_films()
        for f in films:
            if f.id == film_id:
                return f
        return None

    def __str__(self):
        return str(self.id)+'\t'+self.name+'\t'+self.sortie

    def get_upcoming_seances(self, cine_id):
        seances = self.get_seances(cine_id)
        present = datetime.now(timezone('UTC'))
        upcoming_seances = [s for s in seances if s.timestamp > present]
        return sorted(upcoming_seances, key=lambda seance: seance.timestamp)  # sort by timestamp

    def get_today_upcoming_seances(self, cine_id):
        seances = self.get_seances(cine_id)
        present = datetime.now(timezone('UTC'))
        present_local = datetime.now(get_localzone())
        today_upcoming_seances = [s for s in seances if s.timestamp > present and s.timestamp.date() == present_local.date()]
        return sorted(today_upcoming_seances, key=lambda seance: seance.timestamp)  # sort by timestamp

    def get_upcoming_seances_of_the_week(self, cine_id):
        seances = self.get_seances(cine_id)
        present = datetime.now(timezone('UTC'))
        present_local = datetime.now(get_localzone())
        upcoming_seances = [s for s in seances if s.timestamp > present and s.timestamp.date().timetuple().tm_yday < ((present_local.date().timetuple().tm_yday + 7)%365)]
        return sorted(upcoming_seances, key=lambda seance: seance.timestamp)  # sort by timestamp
