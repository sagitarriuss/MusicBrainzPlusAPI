import re
import datetime as dt
import musicbrainzngs as mb
from database import MusicDatabase

SEARCH_RECS_LIMIT = 100  # Only values between 1 and 100 (both inclusive) are allowed. If not given, default is 25

# The extra versions of songs and albums will be skipped
EXTRA_VERSION_WORDS = ("remix", "mix", "version", "edition", "revised", "acoustic", "live", "medley", "bootleg",
                       "stripped", "radio", "idea", "reprise", "track", "commentary")


class MusicBrainzLoader:
    """ The class to request MusicBrainz API, retrieve required data from response, and load them to own music DB. """

    def __init__(self):
        """ Prepare for MusicBrainz API request, response processing, data loading to DB. """
        self.__mdb = None  # DB will be connected after parsing data
        self.__temp_songs = None
        mb.set_useragent("MusicBrainzPlusAPI", "1.0", "https://github.com/sagitarriuss")

    @staticmethod
    def get_song_load_priority(song_album) -> int:
        """ Prioritize the collected song album to select the best matching within duplicated songs. """
        if song_album[2] == 'Album' and song_album[3] != "XW":  # album release type and country is artist's country
            return 1
        elif song_album[2] == 'Album':  # album release type
            return 2
        elif song_album[3] != "XW":  # release country is artist's country
            return 3
        else:
            return 4

    def add_song_to_db(self, song_code, song_title, song_album, song_length) -> bool:
        """ After requests processing, add the collected song information to temp table in own DB, avoid duplicates. """
        if song_code not in self.__temp_songs:

            if not self.__mdb:
                self.__mdb = MusicDatabase()
                self.__mdb.create_song_temp_table()

            priority = self.get_song_load_priority(song_album)
            album_name = song_album[0] if song_album[2] != "Single" else "<Single>"  # release-group type is checked

            self.__mdb.insert_song_data_temp(song_code,
                                             song_title.replace("’", "'"),  # different apostrophe symbols are present
                                             album_name,
                                             song_album[1],  # album date
                                             song_length,
                                             priority)

            self.__temp_songs.append(song_code)

            return True
        else:
            return False

    @staticmethod
    def convert_release_date(release_date) -> dt.date:
        """ Parse date information for release as full date or just a year, release with empty date will be skipped. """
        if len(release_date) == 4:
            return dt.date(int(release_date), 12, 31)  # the end of year to try to find earlier dates
        elif len(release_date) == 10:
            return dt.datetime.strptime(release_date, '%Y-%m-%d').date()
        else:  # no date, skip the release
            return dt.date.max

    @staticmethod
    def has_country_in_events(release_events, release_country) -> bool:
        """ Check if required release country code is present in the release event list. """
        for event in release_events:
            if release_country in event['area']['iso-3166-1-code-list']:
                return True
        return False

    @classmethod
    def is_extra_version(cls, title, in_brackets=True) -> bool:
        """ Check if song or album is a different version of the original by text inside ending brackets or anywhere."""
        if in_brackets:
            if "(" in title and ")" in title:
                text_in_brackets = re.findall(r'\(.*?\)', title)
                if text_in_brackets:
                    return cls.is_extra_version(text_in_brackets[-1], False)  # the last brackets are checked
        else:
            title_lower = title.lower()
            for extra_word in EXTRA_VERSION_WORDS:  # constant tuple of indicating keywords defined on top
                if extra_word in title_lower:
                    return True
        return False

    @classmethod
    def get_first_song_release(cls, releases, release_country, release_type, release_primary_type=""):
        """ Retrieve original release attributes by type/country to find release where the song was introduced."""
        first_release_name = ""
        first_release_type = ""
        first_release_date = dt.date.max

        for release in releases:

            if 'status' in release and release['status'] == "Official" and not cls.is_extra_version(release['title']):

                release_group = release['release-group']
                if ((not release_type or 'type' in release_group and release_type == release_group['type']) and
                    (not release_primary_type or 'primary-type' in release_group
                     and release_primary_type == release_group['primary-type'] and release_group['type'] != "Live")):

                    if ('country' in release and release['country'] == release_country or
                            'release-event-list' in release and cls.has_country_in_events(
                                release['release-event-list'], release_country)):

                        release_date = cls.convert_release_date(release['date'])
                        if release_date < first_release_date:
                            first_release_date = release_date
                            first_release_name = release['title']
                            first_release_type = release_group['type']

        if not first_release_name and release_type:  # if not found try to search in primary-type
            first_release = cls.get_first_song_release(releases, release_country, "", release_type)
        else:
            first_release = None

        # if album release still not found in artist's country try to search in released in Worldwide area
        if not first_release_name and not first_release and release_country != "XW":
            first_release = cls.get_first_song_release(releases, "XW", release_type, release_primary_type)

        if first_release_name:
            return first_release_name, first_release_date, first_release_type, release_country
        else:
            return first_release

    def load_songs_by_arid(self, arid, exact_artist_name, artist_country, offset=0, total_count=0, added_counts=None):
        """ Request MusicBrainz API for all songs of the exact artist and process the response for loading to DB. """
        added_count = 0

        # max limit is 100, but we need to process all the recordings as result page by page
        search_result = mb.search_recordings(arid=arid, offset=offset, limit=SEARCH_RECS_LIMIT)

        if total_count == 0:
            total_count = search_result['recording-count']

        if total_count > 0:
            search_result = search_result['recording-list']

            for song in search_result:

                if (not self.is_extra_version(song['title']) and  # skip extra version based on the tuple of words
                   ('disambiguation' not in song or not self.is_extra_version(song['disambiguation'], False))):

                    song_length = int(song['length']) if 'length' in song else None
                    song_releases = song['release-list'] if 'release-list' in song else None

                    if song_length and song_releases:  # there is a bug in MB API when length or releases are missing
                        song_album = self.get_first_song_release(song_releases, artist_country, "Album")

                        if not song_album:  # if not found try to search in Singles, possibly the song is just released
                            song_album = self.get_first_song_release(song_releases, artist_country, "Single")

                        if song_album:  # if no album/single this may be video/live recording of the prior song, skip it
                            self.add_song_to_db(song['id'], song['title'], song_album, song_length)
                            added_count += 1
        else:
            return f"Nothing found for artist {arid} - {exact_artist_name}."

        if added_counts is None:
            added_counts = [added_count]
        else:
            added_counts.append(added_count)

        if total_count > SEARCH_RECS_LIMIT and offset + len(search_result) < total_count:
            return self.load_songs_by_arid(arid, exact_artist_name, artist_country, offset + SEARCH_RECS_LIMIT,
                                           total_count, added_counts)  # process next page of recordings by recursion
        elif sum(added_counts) > 0:
            load_count = self.__mdb.load_song_data_from_temp_table(exact_artist_name)
            return f"{load_count} songs successfully loaded to DB for artist {exact_artist_name}."
        else:
            return f"Nothing added to DB for artist {arid} - {exact_artist_name}."

    def load_songs_by_artist(self, artist_name) -> str:
        """ Request MusicBrainz API for the artist, then get all his songs with needed information and load to DB. """
        self.__temp_songs = []

        # additional conditions can be added to the query to get more precise results as needed
        search_result = mb.search_artists(query=f'artist:"{artist_name}"', limit=1)['artist-list']

        if search_result:
            artist = search_result[0]  # the first or one found artist is considered as best matching
            return self.load_songs_by_arid(artist['id'], artist['name'], artist['country'])
        else:
            return f"Artist {artist_name} not found."


if __name__ == "__main__":
    print(MusicBrainzLoader().load_songs_by_artist("Imagine Dragons"))  # Test example for standalone module running
