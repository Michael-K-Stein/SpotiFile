from config import *
from webgui import app
import spotify_mass_download
from spotify_mass_download import full_download, save_globals_save_file
from threading import Thread

def main():
    print(f'Spotify Fuzzer')
    print('\n\n\n')

    spotify_mass_download.g_keep_saving += 1

    save_globals_save_file_thread = Thread(target=save_globals_save_file)
    save_globals_save_file_thread.start()
    app.run(host='127.0.0.1', port=8888, debug=False)

    spotify_mass_download.g_keep_saving -= 1


if __name__ == '__main__':
    main()
