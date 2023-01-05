from config import *
from pydoc import render_doc
from flask import Flask, render_template, request, jsonify
from spotify_mass_download import full_download, console, download_all_categories_playlists
app = Flask(__name__)

app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/actions/download/', methods=['POST'])
def actions_download():
    try:
        spotify_url = request.form.get('flink')
        recursive = request.form.get('recursive') or False
        recursive_artist = request.form.get('recursive-artist') or False
        recursive_album = request.form.get('recursive-album') or False
        recursive_limit = min(int(request.form.get('recursive-limit')) or 1024, FULL_DOWNLOAD_RECURISVE_LIMIT)
        thread_count = min(int(request.form.get('thread-count')) or 5, FULL_DOWNLOAD_THREAD_LIMIT)
        recursive = True if recursive == 'on' else False
        recursive_album = True if recursive_album == 'on' else False
        recursive_artist = True if recursive_artist == 'on' else False
        full_download(DEFAULT_DOWNLOAD_DIRECTORY, spotify_url, recursive=recursive, recursive_artist=recursive_artist, recursive_album=recursive_album, recursive_limit=recursive_limit, thread_count=thread_count)
        return 'success'
    except Exception as ex:
        return str(ex)


@app.route('/actions/download/categories')
def actions_download_categories():
    download_all_categories_playlists()


@app.route('/info/console/')
def info_console():
    offset = request.args.get('offset')
    if offset == 'undefined':
        offset = 0
    offset = int(offset)
    logs = console.get()
    return jsonify( {'logs': logs[offset:], 'offset': len(logs)} )


if __name__ == '__main__':
    app.run(debug=True)
