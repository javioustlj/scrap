from urllib import request, parse
from bs4 import BeautifulSoup
import os
import time
from retrying import retry
import json



def get_episode_path(author, name, num):
    current_path = os.getcwd()
    episode_directory = os.path.join(current_path, author, name)
    try:
        os.makedirs(episode_directory)
    except FileExistsError:
        pass
    episode_name = name + '{0:03d}.mp3'.format(num)
    episode_path = os.path.join(episode_directory, episode_name)
    return episode_path

def write_episode_file(file_path, file_contents):
    with open(file_path, mode='wb') as f:
        f.write(file_contents)

def get_one_episode(episode_url):
    s = parse.unquote(episode_url)
    print(s)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    req = request.Request(episode_url, headers=headers)
    response = request.urlopen(req, timeout=20)
    return response.read()

def get_episode_url(page_url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    req = request.Request(page_url, headers=headers)
    response = request.urlopen(req, timeout=10)
    html = response.read().decode('GBK')
    soup = BeautifulSoup(html, 'lxml')
    a = soup.find(name='a', id='down')
    episode_url = a.attrs['href']
    return episode_url

#url = 'http://www.zgpingshu.com/play/542/'

#headers = {
#    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
#}
#req = request.Request(url, headers=headers)
#response = request.urlopen(req)
#html = response.read().decode('GBK')
#soup = BeautifulSoup(html, 'lxml')

#for x in soup.find_all(name='div', class_='down'):
#    page_url = 'http:' + x.a.attrs['href']
#    print(page_url)
#    episode_url = get_episode_url(page_url)
#    get_one_episode(episode_url)

@retry(stop_max_attempt_number = 1000, wait_fixed=30000)
def process_one_episode(page_url, i, name):
    print(page_url)
    episode_url = get_episode_url(page_url)
    print(episode_url)
    episode = get_one_episode(episode_url)
    episode_path = get_episode_path(author, name, i)
    print(episode_path)
    write_episode_file(episode_path, episode)

def process_one_note(note):
    name = note['name']
    len = note['长度'][0:-1]
    base_url = "http://www.zgpingshu.com/down/{0}/".format(note['id'])
    process_one_episode(base_url, 1, name)
    for i in range(2, int(len)):
        page_url =  base_url + '{0}.html'.format(i)
        process_one_episode(page_url, i, name)

author = '单田芳'

with open('单田芳.json', mode='r', encoding='utf-8') as f:
    notes = json.loads(f.read())
    for note in notes:
        print(note)
        process_one_note(note)