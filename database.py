import psycopg as pg
import datetime as dt
from configuration import MainAppConfiguration

PG_CONNECTION_STRING_FMT = "dbname={} host={} user={} password={}"


class MusicDatabase:

    def __init__(self):
        config = MainAppConfiguration()

        db_connection_string = PG_CONNECTION_STRING_FMT.format(
            config.get_db_name(),
            config.get_db_host(),
            config.get_db_user(),
            config.get_db_password())

        self.__con = pg.connect(db_connection_string)
        self.__cur = self.__con.cursor()

    def get_song_data(self, song_title):
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
        sql = (f"insert into temp_song_load (song_code, song_title, album_name, album_date, song_length, load_priority)"
               f"values ('{song_code}', $${song_title}$$, $${album_name}$$, '{album_date.strftime('%Y-%m-%d')}',"
               f" '{str(dt.timedelta(seconds=song_length // 1000))}', {load_priority})")
        self.__cur.execute(sql)

    def load_song_data_from_temp_table(self, artist_name):
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
