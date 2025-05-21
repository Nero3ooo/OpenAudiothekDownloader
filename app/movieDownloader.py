import os
import requests
from bs4 import BeautifulSoup
import wget
import json
import argparse
from urllib.parse import urlparse
import logging
from yt_dlp import YoutubeDL
import re

class MovieDownloader:
    logging.basicConfig(format='MovieDownloader:%(levelname)s:%(message)s', level=logging.INFO)

    id = None
    url = ''
    folder = '/movies'

    def __init__(self, uri, id, progress_map, progress_lock):
        logging.info(f"Initializing MovieDownloader with URI: {uri}")
        self.url = uri
        self.id = id
        self.progress_map = progress_map
        self.progress_lock = progress_lock

    def loadMovie(self):
        logging.info(f"Loading movie from {self.url}")
        os.makedirs(self.folder, exist_ok=True)

        def progress_hook(d):
            with self.progress_lock:
                if d['status'] == 'downloading':
                    clean_percent = self.__strip_ansi(d.get('_percent_str', '').strip())
                    logging.info(f"Raw percentage string: {clean_percent}")
                    self.progress_map[self.id] = {
                        "status": "downloading",
                        "progress": clean_percent,
                        "message": f"{d['_percent_str']} at {d['_speed_str']} ETA {d['_eta_str']}"
                    }
                    logging.info(f"Downloading: {d['_percent_str']} at {d['_speed_str']} ETA {d['_eta_str']}")
                elif d['status'] == 'finished':
                    self.progress_map[self.id] = {
                        "status": "finished",
                        "progress": "100%",
                        "message": "Download complete."
                    }
                    logging.info(f"Download finished: {d['filename']}")
                logging.info(f"Progress map updated: {self.progress_map}")

        ydl_opts = {
            'outtmpl': os.path.join(self.folder, '%(title)s.%(ext)s'),
            'format': 'best',
            'progress_hooks': [progress_hook],
            'quiet': True,  # Show full yt-dlp output
            'noprogress': True,  # Disable progress bar
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            logging.info(f"Movie downloaded successfully to {self.folder}")
            return True
        except Exception as e:
            logging.error(f"Error downloading movie: {str(e)}")
            return f"Download error: {e}"
    
    def __strip_ansi(self, percent_str):
         # Remove ANSI codes
        no_ansi = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
        # Extract decimal number followed by %
        match = re.search(r'(\d{1,3}(?:\.\d+)?)%', no_ansi)
        if match:
            return float(match.group(1))
        return 0.0
