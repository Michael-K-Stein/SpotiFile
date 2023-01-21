import eyed3
import requests
from requests import Response
import hashlib
import datetime
import os
import shutil
import json
from utils.spotify_album import SpotifyAlbum
from utils.spotify_artist import SpotifyArtist
from utils.deezer_utils import Deezer
from utils.utils import clean_file_path
from exceptions import SpotifyTrackException


class SpotifyTrack:
    title = ''
    spotify_id = ''
    artist = ''
    artists = []
    album = None
    thumbnail_href = ''
    release_date = 0
    disc_number = 0
    duration_ms = 0
    explicit = False
    href = ''
    popularity = 0
    audio = b''
    lyrics = ''
    thumnail = b''
    data_dump = ''
    isrc = ''

    def __init__(self, track_data=None) -> None:
        if track_data is not None:
            self.load_from_data(track_data)

    def load_from_data(self, data):
        if 'track' in data:
            data = data['track']
        self.data_dump = data
        self.album = SpotifyAlbum(data['album'])
        self.title = data['name']
        self.spotify_id = data['id']
        self.artists = [SpotifyArtist(x) for x in data['artists']]
        self.thumbnail_href = self.album.thumbnail_href
        self.release_date = self.album.release_date
        self.track_number = data['track_number']
        self.duration_ms = data['duration_ms']
        self.explicit = data['explicit']
        self.href = data['href']
        self.popularity = data['popularity']
        if 'isrc' in data['external_ids']:
            # isrc is not available for local files
            self.isrc = data['external_ids']['isrc']

    def __str__(self) -> str:
        return f'SpotifyTrack< {self.title} >'

    def __repr__(self) -> str:
        return self.__str__()

    def get_lyrics(self, scraper) -> str:
        if scraper is None:
            raise SpotifyTrackException('SCAPER NOT AVAILABLE!')
        return scraper.get_lyrics(self.spotify_id)
    
    def download_thumbnail(self, scraper) -> bytes:
        return scraper.get(self.thumbnail_href).content

    def get_download_link(self, scraper) -> str:
        if not self.isrc:
            return ''
        return Deezer.get_track_download_url(Deezer.get_track_data(Deezer.get_track_id_from_isrc(self.isrc)))[0]

    def download(self, scraper) -> bytes:
        if not self.isrc:
            raise SpotifyTrackException(f'Cannot download local file {self.title}!')
        try:
            download_link = self.get_download_link(scraper)
            data = Deezer.decrypt_download_data(requests.get(download_link, headers={'Accept':'*/*'}), self.isrc)
            return data
        except Exception as ex:
            raise SpotifyTrackException(f'Failed to download {self.title} | Exception: {ex}')
    
    def package_download(self, scraper):
        self.audio = self.download(scraper)
        self.thumbnail = self.download_thumbnail(scraper)
        self.lyrics = self.get_lyrics(scraper)
    
    def preview_title(self):
        return f'{", ".join([x.name for x in self.artists])} - {self.title} [{self.album.title}]'

    def download_to_file(self, scraper, output_path: str):
        temp_file_path = f'temp/{hashlib.sha1(self.title.encode() + self.album.spotify_id.encode()).hexdigest()}.temp.mp3'
        self.package_download(scraper)
        with open(temp_file_path, 'wb') as f:
            f.write(self.audio)

        audio_file = eyed3.load(temp_file_path)
        audio_file.initTag(version=(2, 4, 0))  # version is important
        audio_file.tag.title = self.title
        audio_file.tag.artist = ';'.join([artist.name for artist in self.artists])
        audio_file.tag.album_artist = self.artists[0].name
        audio_file.tag.album = self.album.title
        audio_file.tag.original_release_date = datetime.datetime.fromtimestamp(self.album.release_date).year
        audio_file.tag.track_num = self.track_number
        audio_file.info.time_secs = self.duration_ms / 1000
        audio_file.tag.images.set(3, self.thumbnail, 'image/jpeg', u'cover')
        audio_file.tag.lyrics.set(str(self.lyrics))
        audio_file.tag.comments.set('', str(self.data_dump))

        audio_file.tag.save()

        full_output_path = output_path + '/' + clean_file_path(self.preview_title()) + '.mp3'
        os.makedirs(os.path.dirname(full_output_path), exist_ok=True)
        shutil.move(temp_file_path, full_output_path)
