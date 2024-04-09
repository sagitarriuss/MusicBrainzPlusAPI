from flask_restful import Resource
from musicbrainz_load import MusicBrainzLoader

class LoadAPI(Resource):

    def __init__(self):
        self.__loader = MusicBrainzLoader()

    def load_songs(self, load_path):
        load_list = load_path.split("/")
        if load_list[0] == "artist":
            if len(load_list) == 2:
                res = self.__loader.load_songs_by_artist(load_list[1])
            elif len(load_list) > 2:
                res = "Incorrect loading path."
            else:
                res = "Artist name is not defined."
        else:
            res = "Songs loading by artist is supported only for now, e.g.: api/load/artist/Imagine Dragons"
        return res

    def get(self, load_path):  # 'get' method is temporary used to simplify testing in a browser address line
        return self.load_songs(load_path)

    def post(self, load_path):
        return self.load_songs(load_path)
