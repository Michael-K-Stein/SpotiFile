from threading import Thread, get_ident
import pickle
from typing import Generator
from spotify_client import SpotifyClient
from spotify_scraper import SpotifyScraper
from config import *
import base64
from time import sleep
from datetime import datetime
import random
from utils.utils import clean_file_path
from utils.spotify_track import SpotifyTrack

client = SpotifyClient(sp_key=SP_KEY, sp_dc=SP_DC)
client.get_me()
scraper = SpotifyScraper(client=client)

g_downloaded_artist_covers = []
g_downloaded_songs = []
g_keep_saving = 0


class Console:
    console_output = []

    def log(self, value: str):
        self.cout(value, 'inherit')
    
    def error(self, value: str):
        self.cout(value, 'rgba(255,30,30,0.9)')

    def info(self, value: str):
        self.cout(value, 'rgba(30,255,255,0.9)')

    def happy(self, value: str):
        self.cout(value, 'rgba(30,255,30,0.9)')

    def cout(self, value: str, color: str):
        self.console_output.append(
            {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'value': value,
                'color': color,
            }
            )

    def get(self):
        return self.console_output

console = Console()


def download_track_list(download_dir: str, track_list: Generator[SpotifyTrack, None, None], recursive_artist: bool=False, recursive_album: bool=False, recursive: bool=False, recursive_limit=1024):
    global g_downloaded_songs, g_downloaded_artist_covers
    my_thread_id = str(get_ident()).zfill(6)
    artist_images_download_dir = f'{download_dir}/{settings.ARTIST_IMAGES_SUB_DIR}'
    downloaded_count = 0
    for track in track_list:
        try:
            if downloaded_count % 20 == 0:
                client.refresh_tokens()
            if track.spotify_id in g_downloaded_songs:
                console.info(f'Thread<{my_thread_id}> | Skipping already downloaded song: {track.title}')
                downloaded_count += 1
                continue
            track_path = f'{download_dir}{clean_file_path(track.artists[0].name)}/{clean_file_path(track.album.title)}'
            track.download_to_file(scraper, track_path)
            console.happy(f'Thread<{my_thread_id}> | Downloaded: {track.preview_title()}')
            g_downloaded_songs.append(track.spotify_id)
            if (recursive_album or recursive):
                download_track_list(download_dir=download_dir, track_list=scraper.scrape_album_tracks(track.album.spotify_id), recursive=False)
            
            for artist in track.artists:
                if artist.spotify_id not in g_downloaded_artist_covers:
                    try:
                        artist_image = artist.download_image(scraper)
                        artist_name = base64.b64encode(artist.name.encode()).decode()
                        with open(f'{artist_images_download_dir}/{artist_name}.jpg', 'wb') as f:
                            f.write(artist_image)
                    except Exception as ex:
                        console.error(str(ex))
                    g_downloaded_artist_covers.append(artist.spotify_id)

                if (recursive_artist or recursive):
                    download_track_list(download_dir=download_dir, track_list=scraper.scrape_artist_tracks(track.artist.spotify_id), recursive=False)
                    if recursive_artist:
                        for album in scraper.scrape_artist_albums(artist.spotify_id):
                            download_track_list(download_dir=download_dir, track_list=scraper.scrape_album_tracks(album['id']), recursive=False)
        except Exception as ex:
            console.error(f'Thread<{my_thread_id}> | Exception: {ex}')
        downloaded_count += 1
        if settings.VERBOSE_OUTPUTS:
            console.log(f'Thread<{my_thread_id}> | Processed {downloaded_count} tracks')


def save_globals_save_file():
    global g_keep_saving, g_downloaded_artist_covers, g_downloaded_songs
    try:
        with open(settings.GLOBALS_SAVE_FILE, 'r') as f:
            data = json.loads(f.read())
            g_downloaded_songs = json.loads(data['songs'])
            g_downloaded_artist_covers = json.loads(data['artists'])
            console.log(f'Loaded {len(g_downloaded_songs)} songs & {len(g_downloaded_artist_covers)} artists')
    except Exception as ex:
        console.error(f'Failed to load globals save file! Exception: {ex}')
        if os.path.exists(settings.GLOBALS_SAVE_FILE):
            console.error(f'To avoid data loss, SpotiFile will now exit.')
            exit(1)
    while g_keep_saving > 0:
        with open(settings.GLOBALS_SAVE_FILE, 'w') as f:
            g_downloaded_songs_json = json.dumps(g_downloaded_songs)
            g_downloaded_artist_covers_json = json.dumps(g_downloaded_artist_covers)
            data = {'songs':g_downloaded_songs_json, 'artists': g_downloaded_artist_covers_json }
            f.write( json.dumps(data) )
        if settings.VERBOSE_OUTPUTS:
            console.log('Saved globals file!')
        sleep(settings.DOWNLOADS_FILE_SAVE_INTERVAL)


def full_download(download_dir: str, identifier: str, recursive_artist: bool=False, recursive_album: bool=False, recursive: bool=False, recursive_limit:int=1024, thread_count:int=5):
    global g_downloaded_songs, g_downloaded_artist_covers, g_keep_saving
    try:
        artist_images_download_dir = f'{download_dir}/{settings.ARTIST_IMAGES_SUB_DIR}'
        os.makedirs(artist_images_download_dir, exist_ok=True)
        os.makedirs(f'temp', exist_ok=True)

        g_keep_saving += 1

        client.refresh_tokens()
        console.log(f'Recieved scrape command on identifier: {identifier}, {recursive=}, {recursive_artist=}, {recursive_album=}, {recursive_limit=}, {thread_count=}')
        download_track_list(download_dir=download_dir, track_list=scraper.scrape_tracks(identifier, console=console), recursive=recursive, recursive_album=recursive_album, recursive_artist=recursive_artist, recursive_limit=recursive_limit)

        console.log(f'Comletely done scraping identifier: {identifier}!')

        g_keep_saving -= 1
    except Exception as ex:
        console.error(f'Full download exception: {ex}')


def download_category_playlists(category_id, category_index, category_ids, download_meta_data_only):
    playlist_ids = scraper.get_category_playlist_ids(category_id)
    random.shuffle(playlist_ids)
    for playlist_index, playlist_id in enumerate(playlist_ids):
        console.log(f'Scraping playlist data from playlist {playlist_id} ({playlist_index + 1}/{len(playlist_ids)}) from category {category_id} ({category_index + 1}/{len(category_ids)})')
        try:
            playlist = scraper.get_playlist(playlist_id)
            playlist.export_to_file()
            if not download_meta_data_only:
                full_download(f'{settings.DEFAULT_DOWNLOAD_DIRECTORY}', identifier=playlist.href, thread_count=15)
        except Exception as ex:
            console.error(f'Scraping categories exception: {ex}')


def download_all_categories_playlists(download_meta_data_only=True, query:str=''):
    client.refresh_tokens()
    os.makedirs(f'{settings.DEFAULT_DOWNLOAD_DIRECTORY}/{settings.PLAYLIST_METADATA_SUB_DIR}/', exist_ok=True)
    console.log(f'Scraping playlists from "{query}" categories')
    categories = scraper.get_categories_full(query=query)
    threads = []
    random.shuffle(categories)
    for category_index, category in enumerate(categories):
        console.log(f'Scraping playlists from category {category.name} ({category_index + 1}/{len(categories)})')
        category.download_metadata(scraper=scraper)
        try:
            thread = Thread(target=download_category_playlists, args=(category.spotify_id, category_index, categories, download_meta_data_only))
            thread.start()
            threads.append(thread)
        except Exception as ex:
                console.error(f'Scraping categories exception: {ex}')

    [x.join() for x in threads]
