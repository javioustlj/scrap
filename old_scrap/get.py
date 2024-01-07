from urllib import request, parse
from bs4 import BeautifulSoup
import json
import os
import time
from retrying import retry

def write_json_file(json_path, content):
    with open(json_path, mode='w+', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False, sort_keys=True, indent=4))

def read_json_file(json_path):
    with open(json_path, mode='r', encoding='utf-8') as f:
        contents = json.loads(f.read())
    return contents

@retry(stop_max_attempt_number = 1000, wait_fixed=30000)
def get_episode_download_url(episode_url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    req = request.Request(episode_url, headers=headers)
    response = request.urlopen(req, timeout=10)
    html = response.read().decode('GBK', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    a = soup.find(name='a', id='down')
    download_url = a.attrs['href']
    print(download_url)
    return parse.unquote(download_url)

@retry(stop_max_attempt_number = 1000, wait_fixed=30000)
def get_episode_urls(base_url):
    episode_urls = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    req = request.Request(base_url, headers=headers)
    response = request.urlopen(req, timeout=10)
    html = response.read().decode('GBK', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    divs = soup.find_all(name='div', class_='down')
    for div in divs:
        episode_urls.append('http:' + div.a.attrs['href'])
    return episode_urls

def process_one_work(work, configuration_directory):
    print(work)
    base_url = "http://www.zgpingshu.com/down/{0}/".format(work['id'])
    M = {}
    episode_urls = get_episode_urls(base_url)
    for episode_url in episode_urls:
        print(episode_url)
        download_url = get_episode_download_url(episode_url)
        if (episode_url[-5:] == '.html'):
            s = episode_url.split('/')[-1]
            i = int(s.split('.')[0])
        else:
            i = 1
        M[i] = download_url
        print(i, '\t', download_url)
    work['urls'] = M

    configuration_name = work['name'] + 'json'
    configuration_path = os.path.join(configuration_directory, configuration_name)
    write_json_file(configuration_path, work)

def parse_boxs(boxs):
    print('parse_boxs')
    item = {}
    title = boxs.find(name='div', class_='title')
    # id
    num = 0
    for s in title.a.attrs['href'].split('/'):
        if (s.isdigit()):
            num = int(s)
    item['id'] = num

    # name
    item['name'] = title.get_text()

    # img
    image_url = 'http:' + boxs.img.attrs['src']
    item['image'] = image_url

    # 长度、比特率、大小、状态
    for line in boxs.ul.get_text().splitlines():
        if line in ['\n', '\r\n']:
            continue
        if line.strip() == '':
            continue
        tmp = line.split('：')
        item[tmp[0]] = tmp[1]
    return item

@retry(stop_max_attempt_number = 1000, wait_fixed=30000)
def parse_one_page(page_url, works):
    print('parse_one_page')
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    req = request.Request(page_url, headers=headers)
    response = request.urlopen(req)
    html = response.read().decode('GBK', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    for boxs in soup.find_all(name='div', class_='boxs'):
        works.append(parse_boxs(boxs))
    return soup

def parse_one_author(author, author_url):
    print('parse_one_author')
    works = []
    next_page_url = author_url
    while True:
        print('parse ' + next_page_url)
        soup = parse_one_page(next_page_url, works)
        tmp = soup.find(text='下一页')
        if tmp:
            a = tmp.parent
            next_page_url = 'http:' + a.attrs['href']
        else:
            break
    return works

def create_author_directory(author):
    current_path = os.getcwd()
    author_directory = os.path.join(current_path, author)
    image_directory = os.path.join(author_directory, 'image')
    configuration_directory = os.path.join(author_directory, 'configuration')
    audio_directory = os.path.join(author_directory, 'audio')
    try:
        os.makedirs(author_directory)
        os.makedirs(image_directory)
        os.makedirs(configuration_directory)
        os.makedirs(audio_directory)
    except FileExistsError:
        pass
    directories = {'author_directory' : author_directory,
                   'image_directory' : image_directory,
                   'configuration_directory' : configuration_directory,
                   'audio_directory' : audio_directory}
    return directories

def process_one_author(author, author_url):
    directories = create_author_directory(author)
    #works = parse_one_author(author, author_url)
    works_path = os.path.join(directories['author_directory'], 'works.json')
    #write_json_file(works_path, works)
    works = read_json_file(works_path)
    for work in works:
        process_one_work(work, directories['configuration_directory'])

author = "单田芳"
url = 'https://shantianfang.zgpingshu.com/'
process_one_author(author, url)
