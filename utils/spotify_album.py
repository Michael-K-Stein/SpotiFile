import datetime
import time


class SpotifyAlbum:
    title = ''
    thumbnail_href = ''
    track_count = 0
    release_date = 0
    spotify_id = ''

    def __init__(self, album_data=None) -> None:
        if album_data is not None:
            self.load_from_data(album_data)

    def load_from_data(self, data):
        self.title = data['name']
        self.thumbnail_href = data['images'][0]['url']
        self.track_count = data['total_tracks']
        try:
            self.release_date = time.mktime(datetime.datetime.strptime(data['release_date'], "%Y-%m-%d").timetuple())
        except:
            try:
                self.release_date = time.mktime(datetime.datetime.strptime(data['release_date'], "%Y-%m").timetuple())
            except:
                try:
                    self.release_date = time.mktime(datetime.datetime.strptime(data['release_date'], "%Y").timetuple())
                except:
                    self.release_date = '0000-00-00'
        self.spotify_id = data['id']

    def __str__(self) -> str:
        return f'SpotifyAlbum< {self.title} >'

    def href(self) -> str:
        return f'https://api.spotify.com/v1/albums/{self.spotify_id}'
