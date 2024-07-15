[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Reference Documentation](http://img.shields.io/badge/doc-reference-blue.svg)](https://github.com/sagitarriuss/MusicBrainzPlusAPI/tree/main/docs)

# MusicBrainz Plus REST API

A Python-based API for accessing and populating own PostgreSQL DB with particular [MusicBrainz](https://musicbrainz.org) website data.

The latest version can always be found at https://github.com/sagitarriuss/musicbrainzplusapi

## Minimum Requirements

* Python v3.8

## Documentation
Development report about the API is available [here](https://github.com/sagitarriuss/MusicBrainzPlusAPI/blob/main/docs/mbp_api_dev_report.md).

Developed using [PyCharm 2023.3](https://www.jetbrains.com/pycharm) from [JetBrains s.r.o](https://www.jetbrains.com/).

## Build / Run process

### Docker Compose running (recommended)

If Docker is present, and it's acceptable to automatically run both application and database services within containers, run the single command below (in the *MusicBrainzPlusAPI* directory):
- `docker compose up`

It will automatically download the latest official Docker images for Python 3.11 and PostgreSQL 15 as a base. The local port 7000 will be accessible for connections to use the API application.

In this case, the next setup/running steps are not needed and may be skipped.

### Initial configuration

1) The application settings (music DB parameters) are located in the `MusicBrainzPlusAPI/settings.ini` file and should be manually updated with the dedicated PostgreSQL server values.
2) The DB password is stored in the `MusicBrainzPlusAPI/music_db_pwd.txt` file (the filename is defined above), which is generated automatically if missing. It should be manually updated with the actual value.

### Database setup

The music database is automatically created and initialized by the API application (on first start) on the dedicated PostgreSQL server by the following SQL script (user actions are not required):
- `MusicBrainzPlusAPI/DB/init_music_db.sql`

For an external DB server or if Docker is used only for the API, the PostgreSQL server configuration should include an [authentication record](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html) in the `pg_hba.conf` file for the actual IP address, which is defined in `settings.ini` above, like the line:
- `host all all 192.168.1.5/32 md5`

### Docker image build

If Docker is needed just to run the API, create its image by the command (in the *MusicBrainzPlusAPI* directory):
- `docker build . -t mbp_api`

### Docker container running

If the Docker image is ready then run the API server within a container by the command:
- `docker run -p 7000:7000 mbp_api`

The local port 7000 will be accessible for connections to use the API application.

In this case, the next setup/running steps are not needed and may be skipped.

### Python packages setup

If local Python is used the following extra Python packages (from [PyPI](https://pypi.org)) should be installed by the command:
- `pip install psycopg flask flask_restful musicbrainzngs`

### Running API as a server (console application)

- Run `python main.py` in the *MusicBrainzPlusAPI* directory if local Python is ready.
<br>__OR__
- Download `Release_Windows_x64.zip` from [Releases](https://github.com/sagitarriuss/MusicBrainzPlusAPI/releases) on GitHub, unpack and run `MusicBrainzPlusAPI.exe` (near `settings.ini` file).

### Running DB populating with recordings of one artist as a standalone script

This function can also be run via the API below.

1) Modify the last line in `MusicBrainzPlusAPI/musicbrainz_load.py` with the required artist name in quotes.
2) Run `python musicbrainz_load.py` in the *MusicBrainzPlusAPI* directory.

## Using API

### In any web browser:

1) Go to `http://localhost:7000/api/load/artist/<str>` where `<str>` is the artist/group name to get and populate information about all his songs into DB.

    - After the second run, the information will be requested again from MusicBrainz website and renewed in DB. Sometimes the external MusicBrainz API returns incomplete data about the artist's recordings. The number of the loaded recordings is shown in response. So, try to repeat the loading process a few times to get a maximum of the data for the artist (stop when max number is shown, 100+ for Imagine Dragons).

2) Go to `http://localhost:7000/api/song/<str>` where `<str>` is the song title to show its information for available artists in DB.

    - Case doesn't matter when searching for a song title.

### In command-line interface (CLI):

Each space in `<str>` must be replaced by `%20` character code to use in CLI. Trailing `%` character or `%25` character code in `<str>` means a request for all songs beginning with the defined word(s). The `%25` code may also be leading to search songs ending with or containing the defined word(s).

1) Run `curl -X POST http://localhost:7000/api/load/artist/<str>` to get the artist's songs information and populate it into DB.

2) Run `curl http://localhost:7000/api/song/<str>` to show song information for available artists in DB.

### URL examples for API requests (for web browser or CLI):

- http://localhost:7000/api/load/artist/Imagine%20Dragons
- http://localhost:7000/api/load/artist/Queen
- http://localhost:7000/api/song/Demons
- http://localhost:7000/api/song/we%20are%25