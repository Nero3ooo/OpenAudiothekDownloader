"""
first install the following libraries with pip:

pip install requests
pip install bs4
pip install wget
"""

import os
import requests
from bs4 import BeautifulSoup
import wget
import json
import argparse
from urllib.parse import urlparse

# Instantiate the parser
parser = argparse.ArgumentParser(description='Downloader for ARD Audiothek Audiobooks')

# Required positional argument
parser.add_argument('url', type=str,
                    help='Url of first episode')

args = parser.parse_args()

# get url and path from uri
parsed_uri = urlparse(args.url)
url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
path = parsed_uri.path

def loadEpisode(path):
    r = requests.get(url+path)

    soup = BeautifulSoup(r.content, 'html.parser')

    script = soup.find(id='__NEXT_DATA__')
    json_object = json.loads(script.contents[0])
    # print(json.dumps(json_object, indent=4))
    data = json_object['props']['pageProps']['initialData']['data']

    # load from first episode
    if 'item' in data:
        downloadTitle(data['item'])

        # recursively download next episodes
        next_episode = data['item']['nextEpisode']
        if not next_episode is None:
            loadEpisode(next_episode['path'])
    
    # load from series site, does not work for the whole series
    else:
        nodes = data['result']['items']['nodes']
        for node in nodes:
            downloadTitle(node)
            # print(node['title'])
            # print(node['audios'][0]['url'])

def downloadTitle(itemNode):
     # get download link
        link = itemNode['audios'][0]['url']
        link = link + "?download=true"

        # get file name
        filename = itemNode['title']
        filename = filename.replace('"','')
        filename = filename.replace('/','-')
        filename = filename.replace(':',' -')
        filename = filename.replace('\t',' ')
        filename = filename.replace('|','-')
        filename = filename.replace('–', '-')
        filename = filename.replace('?', '')
        filename = filename + '.mp3'

        # get folder names
        title = itemNode['programSet']['title']
        title = title.replace('"', '')
        title = title.replace('/', '')
        title = title.replace('?', '')
        title = title.replace(': ', '-')
        title = title.replace(' – ', '-')
        title = title.replace(' - ', '-')
        title = title.replace(' | ', '-')
        title = title.split('-')

        print(filename)
        # print(link)

        # Get the current working directory (cwd)
        cwd = os.getcwd()

        # Create folder structure
        if len(title) == 1:
            filename = os.path.join(cwd, title[0], filename)
        if len(title) >= 2:
            filename = os.path.join(cwd, title[0], title[1], filename)
        
        print(filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # download episode
        wget.download(link, filename)
        print()

loadEpisode(path)
