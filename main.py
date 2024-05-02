from flask import Flask
from flask_restful import Api
from song_api import SongAPI
from load_api import LoadAPI
from database import MusicDatabase

API_SERVER_TITLE = "\nREST API server for accessing and populating own music DB based on MusicBrainz website data.\n"

mbp_app = Flask(__name__)
mbp_api = Api()

mbp_api.add_resource(SongAPI, "/api/song/<string:song_title>")
mbp_api.add_resource(LoadAPI, "/api/load/<path:load_path>")

# noinspection PyTypeChecker
mbp_api.init_app(mbp_app)

if __name__ == "__main__":
    print(API_SERVER_TITLE)
    MusicDatabase().init_music_db()  # checking DB connection on server start and init DB
    mbp_app.run(debug=False, port=7000, host="0.0.0.0")
