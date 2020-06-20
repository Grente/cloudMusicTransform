# -*- coding:utf-8 -*-

import os
import re
import requests
import configparser
import asyncio

class Transform():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.uc_path = ''
        self.mp3_path = ''
        self.id2file = {}  # {mp3 ID: file name}

    def check_config(self):
        try:
            self.config.read('config.ini')
            self.uc_path = self.config.get('缓冲路径', 'UC_PATH')
            self.mp3_path = self.config.get('MP3生成文件路径', 'MP3_PATH')
        except Exception as e:
            raise Warning(str(e))
            print('请检查配置文件config.ini变量 UC_PATH MP3_PATH')
            return False

        if not os.path.exists(self.uc_path):
            print('缓存路径错误: {}'.format(self.uc_path))
            return False
        if not os.path.exists(self.mp3_path):
            print('目标路径错误: {}'.format(self.mp3_path))
            return False

        # 容错处理 防止绝对路径结尾不是/
        if self.uc_path[-1] != '/':
            self.uc_path += '/'
        if self.mp3_path[-1] != '/':
            self.mp3_path += '/'
        return True

    def generate_files(self):
        files = os.listdir(self.uc_path)
        for file in files:
            if file[-3:] == '.uc':  # 后缀uc结尾为歌曲缓存
                song_id = self.get_song_by_file(file)
                if not song_id:
                    continue
                self.id2file[song_id] = self.uc_path + file

    async def on_transform(self):
        tasks = [self.do_transform(song_id, file) for song_id, file in self.id2file.items()]
        await asyncio.gather(*tasks)
        print('finish!!')

    async def do_transform(self, song_id, uc_file):
        with open(uc_file, mode='rb') as f:
            uc_content = f.read()
            mp3_content = bytearray()
            for byte in uc_content:
                byte ^= 0xa3
                mp3_content.append(byte)

            song_name, singer_name = self.get_song_info(song_id)
            mp3_file_name = self.mp3_path + '%s - %s.mp3' % (singer_name, song_name)
            with open(mp3_file_name, 'wb') as mp3_file:
                mp3_file.write(mp3_content)
                print('success {}'.format(mp3_file_name))

    def get_song_by_file(self, file_name):
        match_inst = re.match('\d*', file_name)  # -前面的数字是歌曲ID，例：1347203552-320-0aa1
        if match_inst:
            return match_inst.group()

    def get_song_info(self, song_id):
        try:
            url = 'https://api.imjad.cn/cloudmusic/'  # 请求url例子：https://api.imjad.cn/cloudmusic/?type=detail&id=1347203552
            payload = {'type': 'detail', 'id': song_id}
            reqs = requests.get(url, params=payload)
            jsons = reqs.json()
            song_name = jsons['songs'][0]['name']
            singer = jsons['songs'][0]['ar'][0]['name']
            return song_name, singer
        except Exception as e:
            raise Warning(str(e))
            return str(song_id), ''


if __name__ == '__main__':
    transform = Transform()
    if not transform.check_config():
        exit()
    transform.generate_files()
    asyncio.run(transform.on_transform())
