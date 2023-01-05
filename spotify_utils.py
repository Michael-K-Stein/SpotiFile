from email.mime import audio
import base64
from config import *


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
        #self.href = data['href']

    def __str__(self) -> str:
        return f'SpotifyAlbum< {self.title} >'

    def href(self) -> str:
        return f'https://api.spotify.com/v1/albums/{self.spotify_id}'


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
            raise Exception(f'Artist "{self.name}" has no image!')
        image_response = requests.get(artist_images[0]['url'])
        return image_response.content


class SpotifyTrack:
    title = ''
    spotify_id = ''
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
        self.isrc = data['external_ids']['isrc']

    def __str__(self) -> str:
        return f'SpotifyTrack< {self.title} >'

    def __repr__(self) -> str:
        return self.__str__()

    def get_lyrics(self, scraper) -> str:
        if scraper is None:
            raise Exception('SCAPER NOT AVAILABLE!')
        return scraper.get_lyrics(self.spotify_id)
    
    def download_thumbnail(self, scraper) -> bytes:
        return scraper.get(self.thumbnail_href).content

    def get_download_link(self, scraper) -> str:
        return get_track_download_url(get_deezer_track_data(get_deezer_track_id_from_isrc(self.isrc)))[0]

    def decrypt_download_data(self, content: Response) -> bytes:
        chunk_size = 2048
        data_iter = content.iter_content(chunk_size)
        i = 0
        decrypted = b''
        blowfish_key = get_blowfish_key(get_deezer_track_id_from_isrc(self.isrc))
        for chunk in data_iter:
            current_chunk_size = len(chunk)

            if i % 3 > 0:
                decrypted += chunk
            elif len(chunk) < chunk_size:
                decrypted += chunk
                break
            else:
                cipher = Cipher(algorithms.Blowfish(blowfish_key),
                                modes.CBC(
                                    bytes([i for i in range(8)])),
                                default_backend())

                decryptor = cipher.decryptor()
                dec_data = decryptor.update(
                    chunk) + decryptor.finalize()
                decrypted += dec_data

                current_chunk_size = len(dec_data)

            i += 1
        return decrypted

    def download(self, scraper) -> bytes:
        try:
            download_link = self.get_download_link(scraper)
            data = self.decrypt_download_data(requests.get(download_link, headers={'Accept':'*/*'}))
            return data
        except Exception as ex:
            raise Exception(f'Failed to download {self.title} | Exception: {ex}')
    
    def package_download(self, scraper):
        self.audio = self.download(scraper)
        self.thumbnail = self.download_thumbnail(scraper)
        self.lyrics = self.get_lyrics(scraper)
    
    def download_to_file(self, scraper, output_path: str):
        temp_file_path = f'temp/{hashlib.sha1(self.title.encode() + self.album.spotify_id.encode()).hexdigest()}.temp.mp3'
        self.package_download(scraper)
        with open(temp_file_path, 'wb') as f:
            f.write(self.audio)

        audio_file = eyed3.load(temp_file_path)
        audio_file.initTag(version=(2, 4, 0))  # version is important
        audio_file.tag.title = self.title
        audio_file.tag.artist = '/'.join([artist.name for artist in self.artists])
        audio_file.tag.album_artist = '/'.join([artist.name for artist in self.artists])
        audio_file.tag.album = self.album.title
        audio_file.tag.original_release_date = datetime.datetime.fromtimestamp(self.album.release_date).year
        audio_file.tag.track_num = self.track_number
        audio_file.info.time_secs = self.duration_ms / 1000
        audio_file.tag.images.set(3, self.thumbnail, 'image/jpeg', u'cover')
        audio_file.tag.lyrics.set(str(self.lyrics))
        audio_file.tag.comments.set('', str(self.data_dump))

        audio_file.tag.save()

        output_path = clean_file_path(output_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        shutil.move(temp_file_path, output_path)


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

    @property
    def href(self):
        return f'https://open.spotify.com/playlist/{self.spotify_id}'

def get_deezer_track_id_from_isrc(isrc: str) -> str:
    try:
        cookies = {'dzr_uniq_id': 'dzr_uniq_id_frc3270536fa4e8fd6594415125daa7ba2096811'}
        return str(requests.get(f'https://api.deezer.com/2.0/track/isrc:{isrc}').json()['id'])
    except KeyError:
        raise Exception(f'Could not find deezer track by isrc: {isrc}')


def get_deezer_track_data(song_id: str) -> dict:
    cookies = {'dzr_uniq_id': 'dzr_uniq_id_frc3270536fa4e8fd6594415125daa7ba2096811', 'sid': 'fre82a0685d587f159cb7cf0a5f1e8f7aee759d2'}
    resp = requests.post('https://www.deezer.com/ajax/gw-light.php?api_version=1.0&api_token=By7mRaeO.7.UDI6~NtRjcR1whWRStYb4&input=3&method=deezer.pageTrack', data='{"sng_id":"' + song_id +'"}', cookies=cookies)
    track_json = resp.json()
    data = {}
    data['md5_origin'] = track_json['results']['DATA']['MD5_ORIGIN']
    data['media_version'] = track_json['results']['DATA']['media_version'.upper()]
    data['id'] = song_id
    return data


def get_track_download_url(track, **kwargs):
        """Gets and decrypts the download url of the given track in the given quality
        Arguments:
            track {dict} -- Track dictionary, similar to the {info} value that is returned {using get_track()}
        Keyword Arguments:
            quality {str} -- Use values from {constants.track_formats}, will get the default quality if None or an invalid is given. (default: {None})
            fallback {bool} -- Set to True to if you want to use fallback qualities when the given quality is not available. (default: {False})
            renew {bool} -- Will renew the track object (default: {False})
        Raises:
            DownloadLinkDecryptionError: Will be raised if the track dictionary does not have an MD5
            ValueError: Will be raised if valid track argument was given
        Returns:
            str -- Download url
        """

        # Decryption algo got from: https://git.fuwafuwa.moe/toad/ayeBot/src/branch/master/bot.py;
        # and https://notabug.org/deezpy-dev/Deezpy/src/master/deezpy.py
        # Huge thanks!

        quality = track_formats.FLAC
        fallback = True

        try:
            if not "md5_origin" in track:
                raise Exception(
                    "MD5 is needed to decrypt the download link.")

            md5_origin = track["md5_origin"]
            track_id = track["id"]
            media_version = track["media_version"]
        except ValueError:
            raise ValueError(
                "You have passed an invalid argument.")

        def decrypt_url(quality_code):
            magic_char = "¤"
            step1 = magic_char.join((md5_origin,
                                     str(quality_code),
                                     track_id,
                                     media_version))
            m = hashlib.md5()
            m.update(bytes([ord(x) for x in step1]))

            step2 = m.hexdigest() + magic_char + step1 + magic_char
            step2 = step2.ljust(80, " ")

            cipher = Cipher(algorithms.AES(bytes('jo6aey6haid2Teih', 'ascii')),
                            modes.ECB(), default_backend())

            encryptor = cipher.encryptor()
            step3 = encryptor.update(bytes([ord(x) for x in step2])).hex()

            cdn = track["md5_origin"][0]

            return f'https://e-cdns-proxy-{cdn}.dzcdn.net/mobile/1/{step3}'

        url = decrypt_url(track_formats.TRACK_FORMAT_MAP[quality]["code"])
        res = requests.get(url, stream=True)

        if not fallback or (res.status_code == 200 and int(res.headers["Content-length"]) > 0):
            res.close()
            return (url, quality)
        else:
            if "fallback_qualities" in kwargs:
                fallback_qualities = kwargs["fallback_qualities"]
            else:
                fallback_qualities = track_formats.FALLBACK_QUALITIES

            for key in fallback_qualities:
                url = decrypt_url(
                    track_formats.TRACK_FORMAT_MAP[key]["code"])

                res = requests.get(
                    url, stream=True)

                if res.status_code == 200 and int(res.headers["Content-length"]) > 0:
                    res.close()
                    return (url, key)


def get_blowfish_key(track_id):
    secret = 'g4el58wc0zvf9na1'

    m = hashlib.md5()
    m.update(bytes([ord(x) for x in track_id]))
    id_md5 = m.hexdigest()

    blowfish_key = bytes(([(ord(id_md5[i]) ^ ord(id_md5[i+16]) ^ ord(secret[i]))
                           for i in range(16)]))

    return blowfish_key
