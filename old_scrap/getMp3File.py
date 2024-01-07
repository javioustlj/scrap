# -*- coding: utf-8 -*-

import subprocess
import os
import json
import sys

def get_episode_path(author, name, num):
    current_path = os.getcwd()
    episode_directory = os.path.join(current_path, author, 'audio', name)
    try:
        os.makedirs(episode_directory)
    except FileExistsError:
        pass
    episode_name = name + '{0:03d}.mp3'.format(int(num))
    episode_path = os.path.join(episode_directory, episode_name)
    return episode_path

def read_work_json(configuration_path):
    notes = []
    with open(configuration_path, mode='r', encoding='utf-8') as f:
        notes = json.loads(f.read())
    return notes

def download_episode(episode_path, url):
    cmd = "wget --tries=100 \'{0}\' -O \'{1}\'".format(url, episode_path)
    
    subprocess.run([cmd], shell=True)

def process_one_work(configuration_path):
    author = '单田芳'
    work = read_work_json(configuration_path)
    for i,url in work['urls'].items():
        episode_path = get_episode_path(author, work['name'], i)
        print(episode_path)
        download_episode(episode_path, url)

def print_files(path):
    files = []
    files = os.listdir(path)
    for file in files:
        work_configure_path = os.path.join(path, file)
        print(work_configure_path)
        process_one_work(work_configure_path)

print(sys.argv[1])
configuration_path = sys.argv[1]
print(configuration_path)
print_files(configuration_path)