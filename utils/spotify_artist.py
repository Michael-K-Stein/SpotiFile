import requests
from exceptions import SpotifyArtistException


class SpotifyArtist:
    spotify_id = ''
    name = ''

    def __init__(self, artist_data: None) -> None:
        if artist_data is not None:
            self.load_from_data(artist_data)

    def load_from_data(self, data):
        self.spotify_id = data['id']
        self.name = data['name']
    
    def href(self) -> str:
        return f'https://api.spotify.com/v1/artists/{self.spotify_id}'

    def __str__(self) -> str:
        return f'SpotifyArtist< {self.name} >'
    
    def __repr__(self) -> str:
        return self.__str__()

    def download_image(self, scraper) -> bytes:
        if scraper is None:
            return b''
        artist_images = scraper.get(self.href()).json()['images']
        if len(artist_images) == 0:
            raise SpotifyArtistException(f'Artist "{self.name}" has no image!')
        image_response = requests.get(artist_images[0]['url'])
        return image_response.content

    def get_this_is_playlist(self, scraper) -> str:
        if 'this_is_playlist_id' in self.__dict__ and self.this_is_playlist_id:
            return self.this_is_playlist_id
        self.this_is_playlist_id = ''
        this_is = requests.utils.quote(f'this is {self.name}')
        search_results = scraper.get(f'https://api.spotify.com/v1/search?type=playlist&q={this_is}&market=IL').json()
        for playlist_json in search_results['playlists']['items']:
            if playlist_json['name'].lower() != f'this is {self.name}'.lower():
                continue
            if playlist_json['description'].lower() != f'This is {self.name}. The essential tracks, all in one playlist.'.lower():
                continue
            self.this_is_playlist_id = playlist_json['id']
            break
        return self.this_is_playlist_id
