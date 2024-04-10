from flask_restful import Resource
from database import MusicDatabase


class SongAPI(Resource):
    """ Song endpoint implementation for the API to get song information from own music database """

    def __init__(self):
        """ Connects to own database """
        self.__mdb = MusicDatabase()

    def get(self, song_title):
        """ Queries from DB and returns song information by the full or pattern title with % symbol """
        res = self.__mdb.get_song_data(song_title)
        if len(res) != 0:
            return res
        else:
            return f'Song not found: {song_title}.'
