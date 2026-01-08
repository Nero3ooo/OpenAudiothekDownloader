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

    def __init__(self, id, progress_map, progress_lock, cookie_manager=None):
        self.id = id
        self.progress_map = progress_map
        self.progress_lock = progress_lock
        self.cookie_manager = cookie_manager

    def setUrl(self, url):
        logging.info(f"Setting URL: {url}")
        self.url = url

    def download(self):
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

        #ydl_opts = {'subtitleslangs': ['fr'], 'writesubtitles': True}
        ydl_opts = {
            'outtmpl': os.path.join(self.folder, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook]
        }

        # Add cookies if available
        cookie_file_path = None
        if self.cookie_manager and self.cookie_manager.has_cookies():
            # Create Netscape format cookie file for yt-dlp
            cookie_file_path = self.cookie_manager.create_netscape_cookie_file('cookies.txt')
            if cookie_file_path:
                ydl_opts['cookiefile'] = cookie_file_path
                cookies_dict = self.cookie_manager.get_cookies_dict()
                logging.info(f"Using {len(cookies_dict)} cookies from {cookie_file_path} for download")
                logging.info(f"Cookie names: {list(cookies_dict.keys())}")

                # Read and log the cookie file content for debugging
                try:
                    with open(cookie_file_path, 'r') as f:
                        cookie_content = f.read()
                        logging.info(f"Generated cookie file content:\n{cookie_content}")
                except Exception as e:
                    logging.warning(f"Could not read cookie file for debugging: {e}")
            else:
                logging.warning("Failed to create cookie file, proceeding without authentication")

        if(self.url.startswith('https://www.arte.tv/')):
            formats = [
             'VA-STA-3103'
             'VA-STA-2307', 
             'VA-STA-2190',
             'VA-STA-2197', 
             'VA-STA-1614', 
             'VA-STA-919', 
             'VA-STA-424',
            ]
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
            # dont use format just use ffmpeg to download the video
  
        else:
            ydl_opts['format'] = 'best'


        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            logging.info(f"Movie downloaded successfully to {self.folder}")
            return True
        except Exception as e:
            logging.error(f"Error downloading movie: {str(e)}")
            with self.progress_lock:
                self.progress_map[self.id] = {
                    "status": "error",
                    "progress": 0,
                    "message": f"Download error: {str(e)}"
                }
            return f"Download error: {e}"
        finally:
            # Clean up temporary cookie file if it was created
            if cookie_file_path and os.path.exists(cookie_file_path):
                try:
                    os.remove(cookie_file_path)
                    logging.info(f"Cleaned up cookie file: {cookie_file_path}")
                except Exception as e:
                    logging.warning(f"Failed to clean up cookie file: {e}")
    
    def __strip_ansi(self, percent_str):
         # Remove ANSI codes
        no_ansi = re.sub(r'\x1b\[[0-9;]*m', '', percent_str)
        # Extract decimal number followed by %
        match = re.search(r'(\d{1,3}(?:\.\d+)?)%', no_ansi)
        if match:
            return float(match.group(1))
        return 0.0
