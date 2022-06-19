import json
from bs4 import BeautifulSoup
import requests

def get_channel_list():
    
    URL = "https://ustvgo.tv"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="content")
    list_results = results.find_all("a")
   
    channels = []
    for result in list_results:
        code = get_channel_code(result.get("href"))
        m3u = f'https://h5.ustvgo.la/{code}/myStream/playlist.m3u8?wmsAuthSign='
        channels.append({"name": result.text, "url": result.get("href"), "code": code, "m3u": m3u})

    with open('channels.json', 'w') as fp:
        json.dump(channels, fp, indent=4)

def get_channel_code(channel_url):
    headers = {'Referer': 'https://ustvgo.tv/'}
    details = requests.get(channel_url, headers=headers).text
    soup = BeautifulSoup(details, "html.parser")
    results = soup.find(name="iframe", attrs={"allowfullscreen": True})
    code =  results.get("src").split("=")[1]
    return code

def get_wms_Auth_Sign():
    headers = {'Referer': 'https://ustvgo.tv/'}
    sample = requests.get(f'https://ustvgo.tv/player.php?stream=ABC', headers=headers).text

    try:
        return sample.split("hls_src='")[1].split("'")[0].split('wmsAuthSign=')[1]
    except Exception as e:
        print(e)
        return None
def check_link(link):
    try:
        r = requests.head(link)
        return r.status_code == 200
    except Exception as e:
        print(e)
        return False

def create_playlist():
    wmsAuthKey = get_wms_Auth_Sign()
    if wmsAuthKey:
        with open('ustvgo.m3u8', 'w') as fp:
            fp.write('#EXTM3U\n')
            with open('channels.json') as f:
                channels = json.load(f)
                for channel in channels:
                    link = channel["m3u"] + wmsAuthKey
                    if(check_link(link)):
                        fp.write(f'#EXTINF:-1 tvg-id="{channel["code"]}" tvg-group="ustvgo" tvg-name="{channel["name"]}", {channel["name"]}\n')
                        fp.write(f'{link}\n')


def updatedChannels():
    import time
    import os
    if os.path.isfile('channels.json'):
        file_time = os.path.getmtime('channels.json')
        if time.time() - file_time > 86400:
            get_channel_list()
    else:
        get_channel_list()

if __name__ == "__main__":
    updatedChannels()
    create_playlist()

