from flask_restful import Resource
from database import MusicDatabase


class SongAPI(Resource):
    """ Song endpoint implementation for the REST API to get song information from own music database. """

    def __init__(self):
        """ Connect to own database. """
        self.__mdb = MusicDatabase()

    def get(self, song_title):
        """
        GET method implementation for the Song API endpoint.
        Query song information from DB by the full or pattern title with % symbol and return it,
        if found, or 'not found' message.
        """
        res = self.__mdb.get_song_data(song_title)
        if len(res):
            return res
        else:
            return f'Song not found: {song_title}.'
