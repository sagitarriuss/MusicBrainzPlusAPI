# MusicBrainz Plus API Development Report

To be able to get song information from own database for a particular artist, it is necessary to load all song data for the defined artist into the DB in advance. The data source to request all song data is open MusicBrainz API and accessed via musicbrainzngs Python library.

### Search requests to MusicBrainz API

The MusicBrainz API can return data by artist, by recording title (song), release title (album), and by several other search criteria. In the usual search request by the artist's name or recording title, it may return an exactly matched artist or song as well as partially matched (e.g. by one of the words in the request). Therefore it was decided to search for an artist by name using the ‘query’ parameter with the name in quotes for better matching (by **search_artists** method). Although the result can include more than one artist anyway, the first one is the best matching as a rule, and its attributes are used for further data processing.

To load all recordings for the exact artist the **search_recordings** method is used with the ‘arid’ parameter (GUID), which returns a limited number of the recordings including their necessary attributes that are needed in DB. The maximum limit for returned items is 100 which is often less than the total number of recordings for an artist, and so the processing function requests other recordings page by page using the calculated ‘offset’ parameter. The maximum limit is also used to reduce the number of requests to the external API.

### Basic recording processing

Each recording typically includes a song title, length (duration), and a list of various releases. Sometimes, in MusicBrainz API, the recording length or releases are missing in response, so such incomplete recordings will not be processed. Also, to purify song data, the recording is skipped, when it is a special version of the prior original song that may be defined in the song title inside the brackets or in the ‘disambiguation’ attribute. A constant tuple with words indicating a special version, like _remix_, or _edition_, etc. is defined for that.

### Original album lookup in releases

Final information about the song should also include the original album (long-play - **LP**), where the song was introduced. To detect the required album, each release in the list is checked for album type and which was released in the artist’s country (including 'release-event-list' scanning). Special release versions (by the words above) are also skipped. The matched earliest (first) album is selected by the release date.

If the original LP is not found for the recording by the mentioned criteria, the albums are re-processed again by the 'primary-type' attribute of the release, whereas the secondary release type may be a compilation or soundtrack. Live album types are skipped anyway.

If any matching albums are not found for the recording in the artist’s country then the release list is re-processed again to find a Worldwide release (**XW** country) as the recording might have been released originally.

If any LP is not found for the recording then the release list is re-processed again to find at least a ‘Single’ type in the artist’s country, then Worldwide. Possibly the song was just recently introduced and was not included in any album yet, whereas it should be added to the DB to keep most all recordings for the artist nevertheless (with <Single> as the album title).

### Duplicated songs eliminating

However, after processing all the recording data from the MusicBrainz API response the duplicated songs may still appear. The possible duplicated recording IDs (GUID codes) are just detected and skipped during processing. Also, duplicated song titles may appear because the same song may be stored in the MusicBrainz data under different recording IDs with different associated releases, e.g. as a separate soundtrack or single recording in addition to the original song recording already included in the LP album.

To filter out unnecessary duplicated song titles, the collected result song list (in the temp table) is selected by the SQL query based on the priorities (calculated during Python processing) and **row_number** function, and then finally inserted into the permanent DB table. The highest priority is the earliest LP released in the artist's country, then the LP released Worldwide, then any release type in the artist’s country, and any other release is the lowest priority.

### Inconsistent external MusicBrainz API responses

The extra challenge was inconsistent responses of the external MusicBrainz API. Unfortunately, sometimes the API returns essentially less data about the artist's recordings than stored in MusicBrainz. The number of correct consistent recordings with full necessary data varies from one request to another. Currently, this problem is unresolved and may be manually mitigated by a few loading sessions for the artist one by one (request and processing). The number of the loaded recordings is shown and the user is instructed to repeat the loading process a few times to get a maximum of the data for the artist. Some of the possible solutions are reducing the recording limit per request (< 100) that should be evaluated or scraping the MusicBrainz website data themselves, i.e. bypassing the API.
