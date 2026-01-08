import os
import json
import logging
from flask import Flask, render_template, request, send_file, jsonify
import subprocess
import requests
from audioDownloader import AudioDownloader
from movieDownloader import MovieDownloader
from cookieManager import CookieManager
import threading
from uuid import uuid4

logging.basicConfig(format='App:%(levelname)s:%(message)s', level=logging.INFO)


app = Flask(__name__, static_folder='static', static_url_path="/static")

# Global task progress map
progress_map = {}
progress_lock = threading.Lock()

# Global cookie manager
cookie_manager = CookieManager()

@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')

@app.route('/share-handler', methods=['GET'], defaults={'path': ''})
@app.route('/', defaults={'path': ''})
@app.route('/execute', methods=['GET'])
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')

@app.route('/download-show', methods=['POST'])
def downloadShow():
    downloader = AudioDownloader(str(uuid4()),progress_map, progress_lock, recursive=True)
    return __download_with_threading(downloader)
    # threading.Thread(target=downloader.loadShow, args=(), daemon=True).start()

@app.route('/download-episode', methods=['POST'])
def downloadEpisode():
    downloader = AudioDownloader(str(uuid4()),progress_map, progress_lock)
    return __download_with_threading(downloader)
    # threading.Thread(target=downloader.loadEpisode, args=(), daemon=True).start()
    

@app.route('/download-movie', methods=['POST'])
def downloadMovie():
    downloader = MovieDownloader(str(uuid4()),progress_map, progress_lock, cookie_manager=cookie_manager)
    return __download_with_threading(downloader)
    # threading.Thread(target=downloader.loadMovie, args=(), daemon=True).start()

def __download_with_threading(downloader):
    url = json.loads(request.data)
    url = url['textfield']
    if(url == ''):
        result = 'no url'
        return jsonify({'result': result})
    downloader.setUrl(url)
    with progress_lock:
        progress_map[downloader.id] = {"status": "starting", "progress": 0, "message": "Starting download..."}
    threading.Thread(target=downloader.download, args=(), daemon=True).start()
    return jsonify({"result": "Download started.", "task_id": downloader.id})

@app.route("/progress/<task_id>", methods=["GET"])
def get_progress(task_id):
    with progress_lock:
        logging.info(f"Fetching progress for task {task_id}")
        logging.info(progress_map.get(task_id, {"status": "unknown", "progress": 0, "message": "Invalid task ID"})) 
        return jsonify(progress_map.get(task_id, {"status": "unknown", "progress": 0, "message": "Invalid task ID"}))

@app.route('/active-tasks')
def active_tasks():
    with progress_lock:
        # Only return tasks that are not finished or errored
        active = [
            {"task_id": tid, **info}
            for tid, info in progress_map.items()
            if info.get("status") not in ("finished", "error")
        ]
    return jsonify({"tasks": active})

@app.route('/cookies/info', methods=['GET'])
def get_cookie_info():
    """Get information about stored cookies"""
    info = cookie_manager.get_cookie_info()
    return jsonify(info)

@app.route('/cookies/set', methods=['POST'])
def set_cookies():
    """Set cookies from browser string"""
    data = json.loads(request.data)
    cookie_string = data.get('cookies', '')

    if not cookie_string:
        return jsonify({'success': False, 'message': 'No cookies provided'}), 400

    success = cookie_manager.set_cookies_from_string(cookie_string)

    if success:
        info = cookie_manager.get_cookie_info()
        return jsonify({
            'success': True,
            'message': f'Successfully saved {info["count"]} cookies',
            'info': info
        })
    else:
        return jsonify({'success': False, 'message': 'Failed to parse cookies'}), 400

@app.route('/cookies/clear', methods=['POST'])
def clear_cookies():
    """Clear all stored cookies"""
    cookie_manager.clear_cookies()
    return jsonify({'success': True, 'message': 'Cookies cleared'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
