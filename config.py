from urllib.parse import urlencode
from http import client
import requests
from requests import Response
from lxml import html
import json
import datetime, time
import hashlib
import eyed3
import os
import shutil
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pydeezer.constants import track_formats

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
SP_DC = os.getenv('SP_DC')
SP_KEY = os.getenv('SP_KEY')
#PROXY = {"http": "127.0.0.1:8080", "https": "127.0.0.1:8080"}
PROXY = {}
VERIFY_SSL = True


FULL_DOWNLOAD_RECURISVE_LIMIT = 0x4000
FULL_DOWNLOAD_THREAD_LIMIT = 50
VERBOSE_OUTPUTS = False
AUTO_DOWNLOAD_PLAYLIST_METADATA = True

DEFAULT_DOWNLOAD_DIRECTORY = 'music'
ARTIST_IMAGES_SUB_DIR = '_Artists'
PLAYLIST_METADATA_SUB_DIR = '_Playlists'
GLOBALS_SAVE_FILE = '_downloaded_store.json'

def clean_file_path(prompt: str):
    return prompt.replace('?', '').replace('"', '').replace('*', '').replace('|', '').replace('\\', '').replace(':', '').replace('>', '').replace('<', '')
