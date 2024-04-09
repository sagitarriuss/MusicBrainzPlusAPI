from flask import Flask
from flask_restful import Api
from song_api import SongAPI
from load_api import LoadAPI

mbp_app = Flask(__name__)
mbp_api = Api()

mbp_api.add_resource(SongAPI, "/api/song/<string:song_title>")
mbp_api.add_resource(LoadAPI, "/api/load/<path:load_path>")
mbp_api.init_app(mbp_app)

if __name__ == "__main__":
    mbp_app.run(debug=False, port=7000, host="localhost")
