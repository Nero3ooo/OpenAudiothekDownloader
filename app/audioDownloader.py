import os
import requests
from bs4 import BeautifulSoup
import wget
import json
import argparse
from urllib.parse import urlparse
import logging

class AudioDownloader:
    logging.basicConfig(format='AudioDownloader:%(levelname)s:%(message)s', level=logging.INFO)

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
    folder = ''

    def __init__(self, uri):
        parsed_uri = urlparse(uri)
        self.url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        self.path = parsed_uri.path

    def loadShow(self):
        self.__loadEpisode(self.path, True)

    def loadEpisode(self):
        self.__loadEpisode(self.path, False)

    def __loadEpisode(self, path, recursive):
        url = self.url

        if not self.experimentalShow:
            r = requests.get(url+path)
            logging.debug(url+path)
            soup = BeautifulSoup(r.content, 'html.parser')

            script = soup.find(id='__NEXT_DATA__')
            json_object = json.loads(script.contents[0])
            data = json_object['props']['pageProps']['initialData']['data']
            # logging.debug(json.dumps(data, indent=4))

            # load from first episode
            if 'item' in data:
                self.downloadTitle(data['item'])

                # recursively download next episodes
                next_episode = data['item']['nextEpisode']
                logging.debug(json.dumps(next_episode, indent=4))

                if (not next_episode is None and recursive):
                    self.__loadEpisode(next_episode['path'], recursive)
            
            # load from series site, does not work for the whole series
            else:
                nodes = data['result']['items']['nodes']
                for node in nodes:
                    self.downloadTitle(node)
        
        # !! Experimental with GraphQL !!
        else:
            # get programSetId from path
            programSetId = path.split("/")[-2]

            # Provide a GraphQL query
            query = """
            query Query($programSetId: ID!) {
                programSet(id: $programSetId) {
                    items {
                        nodes {
                            title
                            audios {
                                url
                            }
                            programSet {
                                title  
                            }
                        }
                    }
                }
            }
            """

            # Define the programSetId 
            variables = { 
                "programSetId": programSetId 
            }

            # Define the request headers 
            headers = { 
                "Content-Type": "application/json" 
            }

            # Execute the query
            response = requests.post("https://api.ardaudiothek.de/graphql", json={"query": query, "variables": variables}, headers=headers)
            
            # Check the response status code 
            if response.status_code == 200: 
                # Parse the JSON response 
                data = response.json() 
                nodes = data['data']['programSet']['items']['nodes']
                #print(nodes)
                for node in nodes:
                    if len(node['audios'])>0:
                        self.downloadTitle(node)

    def downloadTitle(self, itemNode):
        # get download link
        link = itemNode['audios'][0]['url']
        link = link + "?download=true"

        # get file name
        filename = self.__getFilename(itemNode['title']) 

        # set global folder, if not already set
        if (self.folder == ''):
            # get folder names
            folder = self.__getFoldername(itemNode['programSet']['title'])
            self.folder = folder
        else:
            folder = self.folder
        
        folder = folder.split('-')

        logging.info(filename)
        # print(link)

        # Get the current working directory (cwd)
        # cwd = os.getcwd()
        directory = "/audiobooks"
        # Create folder structure
        if len(folder) == 1:
            filename = os.path.join(directory, folder[0], filename)
        if len(folder) >= 2:
            filename = os.path.join(directory, folder[0], folder[1], filename)
        
        logging.info(filename)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # download episode
        if not self.dryRun:
            wget.download(link, filename)

    def __getFilename(self, filename):
        filename = filename.replace('"','')
        filename = filename.replace('/','-')
        filename = filename.replace(':',' -')
        filename = filename.replace('\t',' ')
        filename = filename.replace('|','-')
        filename = filename.replace('–', '-')
        filename = filename.replace('?', '')
        return  filename + '.mp3'

    def __getFoldername(self, folder):
        folder = folder.replace('"', '')
        folder = folder.replace('/', '')
        folder = folder.replace('?', '')
        folder = folder.replace(': ', '-')
        folder = folder.replace(' – ', '-')
        folder = folder.replace(' - ', '-')
        return folder.replace(' | ', '-')