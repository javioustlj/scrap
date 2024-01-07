from urllib import request, parse
from bs4 import BeautifulSoup
import os
import time
from retrying import retry
import json

def get_episode_url(page_url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    req = request.Request(page_url, headers=headers)
    response = request.urlopen(req, timeout=10)
    html = response.read().decode('GBK', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    a = soup.find(name='a', id='down')
    episode_url = a.attrs['href']
    return parse.unquote(episode_url)


@retry(stop_max_attempt_number = 1000, wait_fixed=30000)
def process_one_episode(page_url, i, M):
    print(page_url)
    episode_url = get_episode_url(page_url)
    print(episode_url)
    M[i] = episode_url

def process_one_note(note):
    name = note['name']
    len = note['长度'][0:-1]
    base_url = "http://www.zgpingshu.com/down/{0}/".format(note['id'])
    M = {}
    process_one_episode(base_url, 1, M)
    for i in range(2, int(len)+1):
        page_url =  base_url + '{0}.html'.format(i)
        process_one_episode(page_url, i, M)
    note['urls'] = M
    with open(name + ".json", mode='w', encoding='utf-8') as f:
        f.write(json.dumps(note, ensure_ascii=False, sort_keys=True, indent=4))


author = '单田芳'

with open('单田芳.json', mode='r', encoding='utf-8') as f:
    notes = json.loads(f.read())
    for note in notes:
        print(note)
        process_one_note(note)