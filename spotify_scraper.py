from concurrent.futures import process
from config import *
from spotify_utils import *
from spotify_client import SpotifyClient
from enum import Enum


class SpotifyScraper:
    _client = None

    class IDTypes(Enum):
        Playlist = 0
        Album = 1
        Artist = 2
        Track = 3
        User = 4
        Unknown = -1

    def __init__(self, sp_dc=None, sp_key=None, client=None) -> None:
        if client is not None:
            self._client = client
        else:
            self._client = SpotifyClient(sp_dc=sp_dc, sp_key=sp_key)

    def identify_link_type(self, link: str) -> IDTypes:
        if 'playlist' in link.lower():
            return self.IDTypes.Playlist
        elif 'album' in link.lower():
            return self.IDTypes.Album
        elif 'artist' in link.lower():
            return self.IDTypes.Artist
        elif 'track' in link.lower():
            return self.IDTypes.Track
        elif 'user' in link.lower():
            return self.IDTypes.User
        return self.IDTypes.Unknown

    def extract_id_from_link(self, link: str) -> str:
        return link[link.rindex('/') + 1:]

    def scrape_tracks(self, link: str, console=None) -> list:
        id_type = self.identify_link_type(link)
        if id_type == self.IDTypes.Playlist:
            return self.scrape_playlist_tracks(self.extract_id_from_link(link))
        elif id_type == self.IDTypes.Album:
            return self.scrape_album_tracks(self.extract_id_from_link(link))
        elif id_type == self.IDTypes.Artist:
            return self.scrape_artist_tracks(self.extract_id_from_link(link), intense=True, console=console)
        elif id_type == self.IDTypes.Track:
            return [SpotifyTrack(self.get(f'https://api.spotify.com/v1/tracks/{self.extract_id_from_link(link)}').json())]
        elif id_type == self.IDTypes.User:
            return self.scrape_user_items(self.extract_id_from_link(link))

    def scrape_playlist(self, playlist_id: str):
        return self._client.get(f'https://api.spotify.com/v1/playlists/{playlist_id}').json()

    def scrape_playlist_tracks(self, playlist_id: str):
        offset = 0
        limit = 100
        playlist_data = self._client.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit={limit}&market=from_token').json()
        tracks = playlist_data['items']
        for track_data in playlist_data['items']:
            yield SpotifyTrack(track_data)
        while playlist_data['next'] is not None:
            offset += limit
            playlist_data = self._client.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?offset={offset}&limit={limit}&market=from_token').json()
            tracks += playlist_data['items']
            for track_data in playlist_data['items']:
                yield SpotifyTrack(track_data)
        if len(tracks) != int(playlist_data['total']):
            print(f'Warning: track count does not match! {len(tracks)} != {int(playlist_data["tracks"]["total"])}')
        for track_data in tracks:
            yield SpotifyTrack(track_data)
        spotify_tracks = [SpotifyTrack(track_data) for track_data in tracks]
        if settings.AUTO_DOWNLOAD_PLAYLIST_METADATA:
            playlist = SpotifyPlaylist(playlist_id, spotify_tracks, self.get_playlist_data(playlist_id))
            playlist.export_to_file()

    def scrape_album(self, album_id: str):
        return self._client.get(f'https://api.spotify.com/v1/albums/{album_id}').json()

    def scrape_album_tracks(self, album_id: str):
        limit = 50
        offset = 0
        ret = self._client.get(f'https://api.spotify.com/v1/albums/{album_id}/tracks?limit={limit}').json()
        for track in ret['items']:
            yield SpotifyTrack(self.get(track['href']).json())
        while ret['next'] is not None:
            offset += limit
            ret = self._client.get(f'https://api.spotify.com/v1/albums/{album_id}/tracks?offset={offset}&limit={limit}').json()
            for track in ret['items']:
                yield SpotifyTrack(self.get(track['href']).json())

    def scrape_artist(self, artist_id: str):
        return self.get(f'https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=from_token').json()

    def scrape_artist_albums(self, artist_id: str):
        offset = 0
        limit = 50
        albums_data = self.get(f'https://api.spotify.com/v1/artists/{artist_id}/albums?market=from_token&limit={limit}&offset={offset}').json()
        albums = albums_data['items']
        while albums_data['next'] is not None:
            offset += limit
            albums_data = self.get(f'https://api.spotify.com/v1/artists/{artist_id}/albums?market=from_token&limit={limit}&offset={offset}').json()
            albums += albums_data['items']
        return albums

    def scrape_artist_tracks(self, artist_id: str, intense:bool=False, console=None):
        tracks = self.scrape_artist(artist_id)['tracks']
        try:
            artist_name = tracks[0]['album']['artists'][0]['name']
        except:
            artist_name = 'Unknown'
        proccessed_tracks = [SpotifyTrack(track_data) for track_data in tracks]
        yield proccessed_tracks
        if intense:
            albums = self.scrape_artist_albums(artist_id)
            proccessed_album_count = 0
            for album in albums:
                for track in self.scrape_album_tracks(album['id']):
                    yield track
                proccessed_album_count += 1
                if console is not None:
                    console.log(f'Scraping {artist_name}\'s albums: {proccessed_album_count} / {len(albums)}')

    def get(self, url: str) -> Response:
        return self._client.get(url)

    def post(self, url: str, payload=None) -> Response:
        return self._client.post(url, payload=payload)

    def get_lyrics(self, track_id: str) -> str:
        try:
            return self.get(f'https://spclient.wg.spotify.com/color-lyrics/v2/track/{track_id}').json()
        except Exception as ex:
            return ''
    
    def get_track_features(self, track_id: str) -> str:
        try:
            return self.get(f'https://api.spotify.com/v1/audio-features/{track_id}').json()
        except Exception as ex:
            return ''

    def get_category_playlist_ids(self, category_id: str, limit=50, offset=0) -> str:
        playlist_ids = []
        current_offset = offset
        has_next = True
        while len(playlist_ids) < limit and has_next:
            category_playlists_json = self.get_category_playlists(category_id, limit=50, offset=current_offset)
            has_next = category_playlists_json['playlists']['next'] is not None
            for playlist in category_playlists_json['playlists']['items']:
                if not playlist:
                    continue
                playlist_ids.append(playlist['id'])
        return playlist_ids

    def get_category_playlists(self, category_id: str, limit:int=50, offset:int=0) -> str:
        data = self.get(f'https://api.spotify.com/v1/browse/categories/{category_id}/playlists/?limit={limit}&offset={offset}').json()
        return data

    def get_categories(self, limit=50) -> str:
        return self.get(f'https://api.spotify.com/v1/browse/categories/?limit={limit}&country=IL').json()

    def get_categories_full(self, limit=50, query:str='') -> list[SpotifyCategory]:
        categories = self.get_categories()
        categories_data = []
        os.makedirs(f'{settings.DEFAULT_DOWNLOAD_DIRECTORY}/{settings.CATEGORY_METADATA_SUB_DIR}/', exist_ok=True)
        for category_json in categories['categories']['items']:
            if not query or query.lower() in category_json['name'].lower(): 
                category = SpotifyCategory(category_json)
                categories_data.append(category)
        return categories_data

    def get_playlist_data(self, playlist_id: str) -> str:
        return self.get(f'https://api.spotify.com/v1/playlists/{playlist_id}').json()

    def get_playlist(self, playlist_id: str) -> str:
        playlist_data = self.get_playlist_data(playlist_id)
        tracks = self.scrape_playlist_tracks(playlist_id)
        return SpotifyPlaylist(spotify_id=playlist_id, tracks=tracks, data=playlist_data)

    def scrape_user_items(self, user_id: str, limit:int=50) -> list[SpotifyTrack]:
        has_next = True
        user_playlists = []
        while has_next:
            user_playlist_set = self.get(f'https://api.spotify.com/v1/users/{user_id}/playlists?limit={limit}').json()
            has_next = user_playlist_set['next']
            for playlist in user_playlist_set['items']:
                user_playlists.append(playlist['id'])
        for playlist_id in user_playlists:
            for track in self.scrape_playlist_tracks(playlist_id):
                yield track
