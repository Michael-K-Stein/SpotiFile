from threading import Thread, get_ident
import pickle
from spotify_client import SpotifyClient
from spotify_scraper import SpotifyScraper
from config import *
import base64
from time import sleep
from datetime import datetime
import random

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


def download_track_list(download_dir: str, track_list: list, recursive_artist: bool=False, recursive_album: bool=False, recursive: bool=False, recursive_limit=1024):
    global g_downloaded_songs, g_downloaded_artist_covers
    my_thread_id = str(get_ident()).zfill(6)
    artist_images_download_dir = f'{download_dir}/{ARTIST_IMAGES_SUB_DIR}'
    downloaded_count = 0
    for track in track_list:
        try:
            if downloaded_count % 20 == 0:
                client.refresh_tokens()
            if track.spotify_id in g_downloaded_songs:
                console.info(f'Thread<{my_thread_id}> | Skipping already downloaded song: {track.title}')
                downloaded_count += 1
                continue
            g_downloaded_songs.append(track.spotify_id)
            track_path = f'{download_dir}/{track.artists[0].name}/{track.album.title}/{", ".join([x.name for x in track.artists])} - {track.title} [{track.album.title}].mp3'
            track.download_to_file(scraper, track_path)
            console.happy(f'Thread<{my_thread_id}> | Downloaded: {track_path}')
            if (recursive_album or recursive) and len(track_list) < recursive_limit:
                new_tracks = scraper.scrape_album_tracks(track.album.spotify_id)
                for new_track in new_tracks:
                    if new_track not in track_list and len(track_list) < recursive_limit:
                        track_list.append(new_track)
                console.log(f'Thread<{my_thread_id}> | Scraped {len(new_tracks)} new songs through recursive album!')
            
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

                if (recursive_artist or recursive) and len(track_list) < recursive_limit:
                    old_size = len(track_list)
                    track_list += scraper.scrape_artist_tracks(artist.spotify_id)
                    if recursive_artist:
                        albums = scraper.scrape_artist_albums(artist.spotify_id)
                        for album in albums:
                            track_list += scraper.scrape_album_tracks(album['id'])
                    console.log(f'Thread<{my_thread_id}> | Scraped {len(track_list) - old_size} new songs through recursive artist!')
        except Exception as ex:
            console.error(f'Thread<{my_thread_id}> | Exception: {ex}')
        downloaded_count += 1
        if VERBOSE_OUTPUTS:
            console.log(f'Thread<{my_thread_id}> | Processed {downloaded_count} / {len(track_list)}')


def save_globals_save_file():
    global g_keep_saving, g_downloaded_artist_covers, g_downloaded_songs
    try:
        with open(GLOBALS_SAVE_FILE, 'r') as f:
            data = json.loads(f.read())
            g_downloaded_songs = json.loads(data['songs'])
            g_downloaded_artist_covers = json.loads(data['artists'])
    except Exception as ex:
        console.error(f'Failed to load globals save file! Exception: {ex}')
    while g_keep_saving > 0:
        with open(GLOBALS_SAVE_FILE, 'w') as f:
            g_downloaded_songs_json = json.dumps(g_downloaded_songs)
            g_downloaded_artist_covers_json = json.dumps(g_downloaded_artist_covers)
            data = {'songs':g_downloaded_songs_json, 'artists': g_downloaded_artist_covers_json }
            f.write( json.dumps(data) )
        if VERBOSE_OUTPUTS:
            console.log('Saved globals file!')
        sleep(15)


def full_download(download_dir: str, identifier: str, recursive_artist: bool=False, recursive_album: bool=False, recursive: bool=False, recursive_limit:int=1024, thread_count:int=5):
    global g_downloaded_songs, g_downloaded_artist_covers, g_keep_saving
    artist_images_download_dir = f'{download_dir}/{ARTIST_IMAGES_SUB_DIR}'
    os.makedirs(artist_images_download_dir, exist_ok=True)
    os.makedirs(f'temp', exist_ok=True)

    g_keep_saving += 1

    client.refresh_tokens()
    console.log(f'Recieved scrape command on identifier: {identifier}, {recursive=}, {recursive_artist=}, {recursive_album=}, {recursive_limit=}, {thread_count=}')
    track_list = scraper.scrape_tracks(identifier, console=console)
    console.log(f'Scraping on identifier: {identifier} yielded {len(track_list)} tracks!')
    download_threads = []
    thread_subsection_size = int(len(track_list) / thread_count)
    for i in range(thread_count - 1):
        download_threads.append(Thread(target=download_track_list, args=(download_dir, track_list[thread_subsection_size * i : (thread_subsection_size * i) + thread_subsection_size], recursive_artist, recursive_album, recursive, recursive_limit)))
        download_threads[-1].start()
        sleep(0.05)
    download_threads.append(Thread(target=download_track_list, args=(download_dir, track_list[thread_subsection_size * (thread_count - 1):], recursive_artist, recursive_album, recursive, recursive_limit)))
    download_threads[-1].start()

    [x.join() for x in download_threads]

    console.log(f'Comletely done scraping identifier: {identifier}!')

    g_keep_saving -= 1


def download_all_categories_playlists(download_meta_data_only=True):
    client.refresh_tokens()
    os.makedirs(f'{DEFAULT_DOWNLOAD_DIRECTORY}/{PLAYLIST_METADATA_SUB_DIR}/', exist_ok=True)
    console.log(f'Scraping playlists from all categories')
    category_ids = scraper.get_categories_ids()
    random.shuffle(category_ids)
    for category_index, category_id in enumerate(category_ids):
        console.log(f'Scraping playlists from category {category_id} ({category_index + 1}/{len(category_ids)})')
        try:
            playlist_ids = scraper.get_category_playlist_ids(category_id)
            for playlist_index, playlist_id in enumerate(playlist_ids):
                console.log(f'Scraping playlist data from playlist {playlist_id} ({playlist_index + 1}/{len(playlist_ids)}) from category {category_id} ({category_index + 1}/{len(category_ids)})')
                try:
                    playlist = scraper.get_playlist(playlist_id)
                    playlist.export_to_file()
                    if not download_meta_data_only:
                        full_download(f'{DEFAULT_DOWNLOAD_DIRECTORY}', identifier=playlist.href)
                except Exception as ex:
                    console.error(f'Scraping categories exception: {ex}')
        except Exception as ex:
                    console.error(f'Scraping categories exception: {ex}')
