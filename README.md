环境：python3.8  
需安装依赖库：  
aiohttp==3.6.2  
aiofiles==0.5.0  

使用方法：  
1、编辑config.py文件配置缓存路径UC_PATH，音乐文件生成路径MP3_PATH（用笔记本编辑就行）  
2、运行transform.py  （cmd命令行输入命令 python transfrom.py） 

转换流程:  
1、对缓存文件的数据和0xa3(163)进行异或(^)运算  
2、用歌曲ID用网易云提供的API去获取歌曲信息  
3、数据保存为mp3文件  

****
2020--6-20  支持并发操作

****
2020--8-16
增加例子
如果安装异步网络模块麻烦，可参考只需requests模块版本
参考：https://blog.csdn.net/haha1fan/article/details/104464221

****
2022--12-30
更新获取歌曲信息接口，用
RUL = 'http://music.163.com/api/song/detail/?id={0}&ids=%5B{1}%5D'.format(song_id, song_id)  
例子：http://music.163.com/api/song/detail/?id=1347203552&ids=%5B1347203552%5D  
