drop table if exists public.song;
create table if not exists public.song (
  song_id     serial       not null,
  song_code   char(36)     not null,
  song_title  varchar(100) not null,
  artist_name varchar(50)  not null,
  album_name  varchar(100) not null,
  song_length time         not null,
  create_date timestamp    not null default current_timestamp,

  constraint pk_song primary key(song_id)
);
create unique index if not exists ind_song_song_title_artist_name on public.song(lower(song_title), lower(artist_name));
create index if not exists ind_song_artist_name on public.song(artist_name);
