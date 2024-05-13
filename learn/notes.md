
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

- 快速实现 FTP 服务器
首先安装 Pyftpdlib 模块
```
 pip install pyftpdlib
```
只要对应目录下执行一下命令，就可以共享该目录了 `ftp://127.0.0.1:2121`
```
python -m pyftpdlib
```

复杂点
```
python -m pyftpdlib -i IP地址 -p 端口 -w -d /root/docs/ -u 用户名 -P 密码
```

- 正则删除空行 
```
 ^\s*\n 替换为空字符串即可
```