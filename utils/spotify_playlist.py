import base64
import json
import requests
import os
from config import settings
from utils.spotify_track import SpotifyTrack


class SpotifyPlaylist:
    spotify_id = ''
    tracks = []
    image_url = ''
    title = ''
    description = ''

    def __init__(self, spotify_id, tracks:list[SpotifyTrack], data):
        self.spotify_id = spotify_id
        self.tracks = tracks
        self.title = data['name']
        self.description = data['description']
        if len(data['images']) > 0:
            self.image_url = data['images'][0]['url']

    def export(self) -> str:
        """ Returns a simple json object with the bare minimum playlist data """
        image_data = requests.get(self.image_url).content
        data = {
            'title': self.title, 
            'description': self.description, 
            'spotify_id': self.spotify_id, 
            'image_url': self.image_url, 
            'image_b64': base64.b64encode(image_data).decode(), 
            'track_ids': [track.spotify_id for track in self.tracks]
            }
        return json.dumps(data)
    
    def export_to_file(self) -> None:
        os.makedirs(f'{settings.DEFAULT_DOWNLOAD_DIRECTORY}/{settings.PLAYLIST_METADATA_SUB_DIR}/', exist_ok=True)
        with open(f'{settings.DEFAULT_DOWNLOAD_DIRECTORY}/{settings.PLAYLIST_METADATA_SUB_DIR}/{self.spotify_id}.playlist', 'w') as f:
            f.write(self.export())

    @property
    def href(self):
        return f'https://open.spotify.com/playlist/{self.spotify_id}'
