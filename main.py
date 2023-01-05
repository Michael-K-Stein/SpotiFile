from config import *
from webgui import app
import spotify_mass_download
from spotify_mass_download import full_download, save_globals_save_file
from threading import Thread
import webbrowser

def main():
    print(f'=== SpotiFile ===')
    spotify_mass_download.g_keep_saving += 1

    save_globals_save_file_thread = Thread(target=save_globals_save_file)
    save_globals_save_file_thread.start()

    webbrowser.open('http://127.0.0.1:8888/')
    app.run(host='127.0.0.1', port=8888, debug=False)

    spotify_mass_download.g_keep_saving -= 1


if __name__ == '__main__':
    main()
