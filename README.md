
环境：python3.8  
依赖库：requests  
使用方法：  
1、配置config.ini文件配置缓存路径UC_PATH，音乐文件生成路径MP3_PATH  
2、运行transform.py  


转换流程:  

1、对缓存文件的数据和0xa3(163)进行异或(^)运算  

2、用歌曲ID用网易云提供的API去获取歌曲信息  

3、数据保存为mp3文件  
