# -*- coding:utf-8 -*-

import os
import re
import configparser
import asyncio
import aiohttp
import aiofiles
import config

class Transform():
    def __init__(self):
        self.uc_path = ''
        self.mp3_path = ''
        self.id2file = {}  # {mp3 ID: file name}

    def check_config(self):
        try:
            self.uc_path = config.UC_PATH
            self.mp3_path = config.MP3_PATH
        except Exception as e:
            print('Warning {} 请检查配置文件config.py变量 UC_PATH MP3_PATH'.format(str(e)))
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

    def on_transform(self):
        loop = asyncio.get_event_loop()
        tasks = [self.do_transform(song_id, file) for song_id, file in self.id2file.items()]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    async def do_transform(self, song_id, uc_file):
        song_name, singer_name = await self.get_song_info(song_id)
        async with aiofiles.open(uc_file, mode='rb') as f:
            uc_content = await f.read()
            mp3_content = bytearray()
            for byte in uc_content:
                byte ^= 0xa3
                mp3_content.append(byte)

            mp3_file_name = self.mp3_path + '%s - %s.mp3' % (singer_name, song_name)
            async with aiofiles.open(mp3_file_name, 'wb') as mp3_file:
                await mp3_file.write(mp3_content)
                print('success {}'.format(mp3_file_name))


    def get_song_by_file(self, file_name):
        match_inst = re.match('\d*', file_name)  # -前面的数字是歌曲ID，例：1347203552-320-0aa1
        if match_inst:
            return match_inst.group()

    async def get_song_info(self, song_id):
        try:
            url = 'https://api.imjad.cn/cloudmusic/?type=detail&id={}'.format(song_id)  # 请求url例子：https://api.imjad.cn/cloudmusic/?type=detail&id=1347203552
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    jsons = await response.json()
                    song_name = jsons['songs'][0]['name']
                    singer = jsons['songs'][0]['ar'][0]['name']
                    return song_name, singer
        except Exception as e:
            print("Warning Song Info", Warning(str(e)))
            return song_id, ''

if __name__ == '__main__':
    transform = Transform()
    if not transform.check_config():
        exit()
    transform.generate_files()
    transform.on_transform()
