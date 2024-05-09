
- 1秒钟启动一个下载服务器

在Python 3中,内置了一个下载服务器,对应目录启动下载服务器，就可以下载该目录的文件, `http://127.0.0.1:8000`
```
python -m http.server
```

- 字符串转换为JSON
使用下面命令可以格式化json数据

```
'{"job": "developer", "name": "lmx", "sex": "male"}' | python -m json.tool
```