[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11-blue.svg)](https://www.python.org/)
[![Reference Documentation](http://img.shields.io/badge/doc-reference-blue.svg)](https://github.com/sagitarriuss/MusicBrainzPlusAPI/tree/main/docs)

# MusicBrainz Plus REST API

A Python-based API for accessing and populating own PostgreSQL DB with particular MusicBrainz website data.

The latest version can always be found at https://github.com/sagitarriuss/musicbrainzplusapi

## Minimum Requirements

* Python v3.8

## Documentation
Development report about the API: [mbp_api_dev_report.md](https://github.com/sagitarriuss/MusicBrainzPlusAPI/blob/main/docs/mbp_api_dev_report.md).

Developed using [PyCharm 2023.3](https://www.jetbrains.com/pycharm) from [JetBrains s.r.o](https://www.jetbrains.com/).

## Build / Run process

### Initial configuration

1) The application settings (music DB parameters) are located in the `MusicBrainzPlusAPI/settings.ini` file and should be manually updated with the dedicated PostgreSQL server values.
2) The DB password is stored in the `MusicBrainzPlusAPI/music_db_pwd.txt` file (the filename is defined above), which is generated automatically if missing. It should be manually updated with the actual value.

### Database setup

By any DB tool (e.g. `psql`) run the following SQL scripts on the dedicated PostgreSQL server:
1) `MusicBrainzPlusAPI/DB/create_music_db.sql` to create/re-create the music database.
2) `MusicBrainzPlusAPI/DB/init_music_db.sql` to create/re-create the database objects (over the newly created DB).

### Python packages setup

The following extra Python packages (from [PyPI](https://pypi.org)) should be installed by the commands:
- `pip install psycopg`
- `pip install flask`
- `pip install flask_restful`
- `pip install musicbrainzngs`

### Running API as a server (console application)

- Run `python main.py` in the MusicBrainzPlusAPI directory.
<br>__OR__
- Download `Release_Windows_x64.zip` from [Releases](https://github.com/sagitarriuss/MusicBrainzPlusAPI/releases) on GitHub, unpack and run `MusicBrainzPlusAPI.exe` (near `settings.ini` file).

### Running DB populating with recordings of one artist as a standalone script

This function can also be run via the API below.

1) Modify the last line in `MusicBrainzPlusAPI/musicbrainz_load.py` with the required artist name in quotes.
2) Run `python musicbrainz_load.py` in the *MusicBrainzPlusAPI* directory.

## Using API

### In any web browser:

1) Go to `http://localhost:7000/api/load/artist/<str>` where `<str>` is the artist/group name to get and populate information about all his recordings into DB.

   - After the second run, the information will be requested again from MusicBrainz website and renewed in DB. Sometimes the external MusicBrainz API returns incomplete data about the artist's recordings. The number of the loaded recordings is shown in response. It makes sense to repeat the loading process a few times to get a maximum of the data for the artist (stop when max number is shown, 100+ for Imagine Dragons).

2) Go to `http://localhost:7000/api/song/<str>` where `<str>` is the song title to show its information for available artists in DB.

   - The song title is case-insensitive to search.

### In command-line interface (CLI):

Each space in `<str>` must be replaced by `%20` character code to use in CLI. Trailing `%` character or `%25` character code in `<str>` means a request for all songs beginning with the defined word(s). `%25` may also be leading to search songs ending with or containing the defined word(s).

1) Run `curl -X POST http://localhost:7000/api/load/artist/<str>` to get the artist's information and populate it into DB.

2) Run `curl http://localhost:7000/api/song/<str>` to show song information for available artists in DB.

### URL examples for API requests (for web browser or CLI):

- http://localhost:7000/api/load/artist/Imagine%20Dragons
- http://localhost:7000/api/load/artist/Queen
- http://localhost:7000/api/song/Demons
- http://localhost:7000/api/song/we%20are%25