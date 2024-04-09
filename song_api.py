from flask_restful import Resource
from database import MusicDatabase


class SongAPI(Resource):

    def __init__(self):
        self.__mdb = MusicDatabase()

    def get(self, song_title):
        res = self.__mdb.get_song_data(song_title)
        if len(res) != 0:
            return res
        else:
            return f'Song not found: {song_title}.'
