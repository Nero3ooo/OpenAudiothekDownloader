import os
import json
import logging
from flask import Flask, render_template, request, send_file, jsonify
import subprocess
import requests
from audioDownloader import AudioDownloader
from movieDownloader import MovieDownloader
import threading
from uuid import uuid4

logging.basicConfig(format='App:%(levelname)s:%(message)s', level=logging.INFO)


app = Flask(__name__, static_folder='static', static_url_path="/static")

# Global task progress map
progress_map = {}
progress_lock = threading.Lock()

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
    url = json.loads(request.data)
    url = url['textfield']
    if(url == ''):
        result = 'no url'
        return jsonify({'result': result})
    downloader = AudioDownloader(url, str(uuid4()),progress_map, progress_lock)
    with progress_lock:
        progress_map[downloader.id] = {"status": "starting", "progress": 0, "message": "Starting download..."}
    threading.Thread(target=downloader.loadShow, args=(), daemon=True).start()
    return jsonify({"result": "Download started.", "task_id": downloader.id})

@app.route('/download-episode', methods=['POST'])
def downloadEpisode():
    url = json.loads(request.data)
    url = url['textfield']
    if(url == ''):
        result = 'no url'
        return jsonify({'result': result})
    downloader = AudioDownloader(url, str(uuid4()),progress_map, progress_lock)
    with progress_lock:
        progress_map[downloader.id] = {"status": "starting", "progress": 0, "message": "Starting download..."}
    threading.Thread(target=downloader.loadEpisode, args=(), daemon=True).start()
    return jsonify({"result": "Download started.", "task_id": downloader.id})

@app.route('/download-movie', methods=['POST'])
def downloadMovie():
    url = json.loads(request.data)
    url = url['textfield']
    if(url == ''):
        result = 'no url'
        return jsonify({'result': result})
    # Run the terminal command
    downloader = MovieDownloader(url,str(uuid4()),progress_map, progress_lock)
    #result = downloader.loadMovie()
    #task_id = str(uuid4())
    with progress_lock:
        progress_map[downloader.id] = {"status": "starting", "progress": 0, "message": "Starting download..."}
    
        logging.info(progress_map.get(downloader.id, {"status": "unknown", "progress": 0, "message": "Invalid task ID"}))
    threading.Thread(target=downloader.loadMovie, args=(), daemon=True).start()
    logging.info(f"Starting download for {downloader.id}")
    return jsonify({"result": "Download started.", "task_id": downloader.id})
    #if(result == True):
    #    result = 'Successfully downloaded movie ' 
    #    result = result + downloader.folder
    #return jsonify({'result': result})  

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
