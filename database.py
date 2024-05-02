import os
import psycopg as pg
import datetime as dt
from psycopg import Connection
from psycopg import sql as pgsql
from configuration import MainAppConfiguration

PG_CONNECTION_STRING_FMT = "dbname={} host={} user={} password={}"


class MusicDatabase:
    """ The class to operate with own PostgreSQL database to insert and get music data. """

    def __init__(self):
        """ Perform connection to the database, configure it and prepare to work. """
        self.__con = None
        self.__cur = None
        self.__config = MainAppConfiguration()
        self.try_connect_or_create_db()

    def connect_db(self, db_name, autocommit=False) -> Connection:
        """ Establish connection to the defined database based on DB parameters in the app configuration. """
        db_connection_string = PG_CONNECTION_STRING_FMT.format(
            db_name,
            self.__config.get_db_host(),
            self.__config.get_db_user(),
            self.__config.get_db_password())
        return pg.connect(db_connection_string, autocommit=autocommit)

    def try_connect_or_create_db(self):
        """ Establish connection to the music database, if it doesn't exist then create it. """
        music_db_name = None  # kill warning
        try:
            music_db_name = self.__config.get_db_name()
            self.__con = self.connect_db(music_db_name)
        except pg.OperationalError as e:
            if f'database "{music_db_name}" does not exist' in str(e):
                with self.connect_db('postgres', True) as pg_con:
                    pg_con.execute(pgsql.SQL('create database ') + pgsql.Identifier(music_db_name))
                self.__con = self.connect_db(music_db_name)
            else:
                raise
        self.__cur = self.__con.cursor()

    def init_music_db(self):
        """ Run the SQL script to initialize the empty/working database, i.e. to create/update the database objects. """
        self.__cur.execute(open(os.path.join(os.path.dirname(__file__), "DB", "init_music_db.sql"), "r").read())
        self.__con.commit()

    def get_song_data(self, song_title):
        """ Query information in DB about the song by its case-insensitive title and returns it as json, if found. """
        sql = (f"select row_to_json(row) from ("
               f"  select song_title"
               f"       , artist_name"
               f"       , album_name"
               f"       , song_length"
               f"    from song"
               f"   where lower(song_title) like $${song_title.lower()}$$) row")
        self.__cur.execute(sql)
        res = self.__cur.fetchall()
        return res

    def create_song_temp_table(self):
        """ Create temporary table in DB to collect all songs for currently processing artist. """
        sql = (f"drop table if exists temp_song_load;"
               f"create temp table temp_song_load ("
               f"  song_code     char(36)     not null,"
               f"  song_title    varchar(100) not null,"
               f"  album_name    varchar(100) not null,"
               f"  album_date    date         not null,"
               f"  song_length   time         not null,"
               f"  load_priority integer      not null,"
               f"  constraint pk_temp_song_load primary key(song_code))")
        self.__cur.execute(sql)

    def insert_song_data_temp(self, song_code, song_title, album_name, album_date, song_length, load_priority):
        """ Insert record to the temporary table in DB with the song information for currently processing artist. """
        sql = (f"insert into temp_song_load (song_code, song_title, album_name, album_date, song_length, load_priority)"
               f"values ('{song_code}', $${song_title}$$, $${album_name}$$, '{album_date.strftime('%Y-%m-%d')}',"
               f" '{str(dt.timedelta(seconds=song_length // 1000))}', {load_priority})")
        self.__cur.execute(sql)

    def load_song_data_from_temp_table(self, artist_name) -> int:
        """
        Copy collected artist's songs information into permanent DB table with elimination of the duplicated titles.
        Return the number of the processed and copied songs for the artist.
        """
        self.__con.commit()
        self.__cur.execute(f"delete from public.song where artist_name = $${artist_name}$$;")
        sql = (f"insert into public.song (song_code, song_title, artist_name, album_name, song_length)"
               f"select song_code, song_title, $${artist_name}$$, album_name, song_length from ("
               f"  select *, row_number() over (partition by lower(song_title) order by load_priority, album_date) pos"
               f"    from temp_song_load) t"
               f" where pos = 1")
        self.__cur.execute(sql)
        self.__con.commit()
        load_count = self.__cur.rowcount
        return load_count
