#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from urllib import request, parse
from bs4 import BeautifulSoup
import json
import os
from retrying import retry
import subprocess


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
}

def write_json_file(json_path, content):
    with open(json_path, mode='w+', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False, sort_keys=True, indent=4))

def read_json_file(json_path):
    with open(json_path, mode='r', encoding='utf-8') as f:
        contents = json.loads(f.read())
    return contents

@retry(stop_max_attempt_number = 1000, wait_fixed=30000)
def fetch_page(url):
    req = request.Request(url, headers=headers)
    response = request.urlopen(req, timeout=10)
    html = response.read().decode('UTF-8', 'ignore')
    return html

def parse_html_page(html):
    soup = BeautifulSoup(html, 'lxml')
    def has_pvideourl(tag):
        return tag.has_attr('pvideourl') and tag.has_attr('columnname') and tag.has_attr('title')
    all_links = soup.find_all(has_pvideourl)
    L = []
    for a in all_links:
        item = {}
        item['title'] = a['title']
        item['url'] = a['pvideourl']
        item['columnname'] = a['columnname']
        L.append(item)
    return L

def create_directory(relative_path):
    current_path = os.getcwd()
    directory = os.path.join(current_path, relative_path)
    try:
        os.makedirs(directory)
    except FileExistsError:
        pass
    return directory

@retry(stop_max_attempt_number = 1000, wait_fixed=30)
def download_mp4(a):
    directory = create_directory(a['columnname'])
    number = a['url'].split('/')[-1][:-4]
    episode_path = os.path.join(directory, number + a['title'] + '.mp4')
    if not os.path.isfile(episode_path):
        cmd = "wget --tries=100 \'{0}\' -O \'{1}\'".format(a['url'], episode_path)
        subprocess.run([cmd], shell=True)

url = 'http://edu.sse.com.cn/college/required/basicinfo/'
html = fetch_page(url)
content = parse_html_page(html)
write_json_file("test.json", content)
for a in content:
    download_mp4(a)

