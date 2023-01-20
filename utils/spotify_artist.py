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
