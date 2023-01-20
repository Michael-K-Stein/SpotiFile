import requests
import base64
import json
from config import settings


class SpotifyCategory:
    name = ''
    spotify_id = ''
    playlist_ids = ''
    thumbnail_href = ''

    def __init__(self, category_data=None):
        self.name = category_data['name']
        self.spotify_id = category_data['id']
        if len(category_data['icons']) > 0:
            self.thumbnail_href = category_data['icons'][0]['url']

    def download_metadata(self, scraper):

        thumbail_b64 = ''
        if self.thumbnail_href:
            thumbail_b64 = base64.b64encode( requests.get(self.thumbnail_href).content ).decode()

        try:
            self.playlist_ids = scraper.get_category_playlist_ids(category_id=self.spotify_id)
        except:
            self.playlist_ids = []

        data = {
            'name': self.name,
            'spotify_id': self.spotify_id,
            'thumbnail_b64': thumbail_b64,
            'playlist_ids': self.playlist_ids,
        }

        with open(f'{settings.DEFAULT_DOWNLOAD_DIRECTORY}/{settings.CATEGORY_METADATA_SUB_DIR}/{self.spotify_id}.category', 'w') as f:
            f.write(json.dumps(data))
