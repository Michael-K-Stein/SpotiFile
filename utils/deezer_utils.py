from config import *
from exceptions import DeezerException


class Deezer:
    _cookies = {'dzr_uniq_id': 'dzr_uniq_id_frc3270536fa4e8fd6594415125daa7ba2096811', 'sid': 'fre82a0685d587f159cb7cf0a5f1e8f7aee759d2'}

    @staticmethod
    def get_track_id_from_isrc(isrc: str) -> str:
        try:
            return str(requests.get(f'https://api.deezer.com/2.0/track/isrc:{isrc}').json()['id'])
        except KeyError:
            raise DeezerException(f'Could not find deezer track by isrc: {isrc}')

    @staticmethod
    def get_track_data(song_id: str) -> dict:
        resp = requests.post('https://www.deezer.com/ajax/gw-light.php?api_version=1.0&api_token=By7mRaeO.7.UDI6~NtRjcR1whWRStYb4&input=3&method=deezer.pageTrack', data='{"sng_id":"' + song_id +'"}', cookies=Deezer._cookies)
        track_json = resp.json()
        data = {}
        data['md5_origin'] = track_json['results']['DATA']['MD5_ORIGIN']
        data['media_version'] = track_json['results']['DATA']['media_version'.upper()]
        data['id'] = song_id
        return data

    @staticmethod
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

    @staticmethod
    def get_blowfish_key(track_id):
        secret = 'g4el58wc0zvf9na1'

        m = hashlib.md5()
        m.update(bytes([ord(x) for x in track_id]))
        id_md5 = m.hexdigest()

        blowfish_key = bytes(([(ord(id_md5[i]) ^ ord(id_md5[i+16]) ^ ord(secret[i]))
                            for i in range(16)]))

        return blowfish_key

    @staticmethod
    def decrypt_download_data(content: Response, isrc: str) -> bytes:
        chunk_size = 2048
        data_iter = content.iter_content(chunk_size)
        i = 0
        decrypted = b''
        blowfish_key = Deezer.get_blowfish_key(Deezer.get_track_id_from_isrc(isrc))
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
