import os
import json
from flask import Flask, render_template, request, send_file, jsonify
import subprocess
import requests
from audioDownloader import AudioDownloader

app = Flask(__name__, static_folder='static', static_url_path="/static")

@app.route('/manifest.json')
def serve_manifest():
    return send_file('manifest.json', mimetype='application/manifest+json')

@app.route('/sw.js')
def serve_sw():
    return send_file('sw.js', mimetype='application/javascript')

@app.route('/', defaults={'path': ''})
@app.route('/execute', methods=['GET'])
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute():
    url = json.loads(request.data)
    url = url['textfield']
    if(url == ''):
        result = 'no url'
        return jsonify({'result': result})
    # Run the terminal command
    downloader = AudioDownloader(url)
    downloader.loadShow()
    result = 'successfully Downloaded '
    result = result + downloader.title
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
