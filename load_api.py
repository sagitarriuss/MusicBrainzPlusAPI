from flask_restful import Resource
from musicbrainz_load import MusicBrainzLoader


class LoadAPI(Resource):
    """ Load endpoint implementation for the REST API to request external music data and load them to own database. """

    def __init__(self):
        """ Prepare external data processor. """
        self.__loader = MusicBrainzLoader()

    def __load_songs(self, load_path) -> str:
        """ Run external songs data request according to input parameters, then processing them, and loading to DB. """
        load_list = load_path.split("/")
        if load_list[0] == "artist":
            if len(load_list) == 2:
                res = self.__loader.load_songs_by_artist(load_list[1])
            elif len(load_list) > 2:
                res = "Incorrect loading path."
            else:
                res = "Artist name is not defined."
        else:
            res = "Songs loading by artist is supported only for now, e.g.: api/load/artist/Imagine%20Dragons"
        return res

    def get(self, load_path):  # 'get' method is temporary used to simplify testing in a browser address line
        """ GET method implementation for the Load API endpoint. Process requested songs and load to DB. """
        return self.__load_songs(load_path)

    def post(self, load_path):
        """ POST method implementation for the Load API endpoint. Process requested songs and load to DB. """
        return self.__load_songs(load_path)
