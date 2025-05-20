import os
import requests
from bs4 import BeautifulSoup
import wget
import json
import argparse
from urllib.parse import urlparse
import logging
from yt_dlp import YoutubeDL


class MovieDownloader:
    logging.basicConfig(format='MovieDownloader:%(levelname)s:%(message)s', level=logging.INFO)

    # Instantiate the parser
    # parser = argparse.ArgumentParser(description='Downloader for ARD Audiothek Audiobooks')

    # Required positional argument
    # parser.add_argument('url', type=str,
    #                    help='Url of first episode')

    # parser.add_argument('--experimentalShow', action=argparse.BooleanOptionalAction, help='If you want to download bigger shows, you can try this. There may be duplicates.')
    # parser.add_argument('--dryRun', action=argparse.BooleanOptionalAction, help='If you just want to list what will be downloaded and where it will be stored.')

    # args = parser.parse_args()

    experimentalShow = False
    dryRun = False
    url = ''
    path = ''
    folder = '/movies'

    def __init__(self, uri):
        logging.info(f"Initializing MovieDownloader with URI: {uri}")
        self.url = uri

    def loadMovie(self):
        logging.info(f"Loading movie from {self.url}")
        os.makedirs(self.folder, exist_ok=True)

        def progress_hook(d):
            if d['status'] == 'downloading':
                logging.info(f"Downloading: {d['_percent_str']} at {d['_speed_str']} ETA {d['_eta_str']}")
            elif d['status'] == 'finished':
                logging.info(f"Download finished: {d['filename']}")

        ydl_opts = {
            'outtmpl': os.path.join(self.folder, '%(title)s.%(ext)s'),
            'format': 'best',
            'progress_hooks': [progress_hook],
            'quiet': False,  # Show full yt-dlp output
            'noprogress': False
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            logging.info(f"Movie downloaded successfully to {self.folder}")
            return True
        except Exception as e:
            logging.error(f"Error downloading movie: {str(e)}")
            return f"Download error: {e}"