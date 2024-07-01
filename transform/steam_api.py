import requests
from requests.adapters import HTTPAdapter

session = requests.Session()
session.mount('http://', HTTPAdapter(max_retries=3))
session.mount('https://', HTTPAdapter(max_retries=3))

def get_cm_list():
    try:
        # 获取 CM (Connection Manager) 服务器列表 用于 Steam 帐户登录认证、好友在线状态、聊天和游戏邀请等等方面 
        # cellid 地区相关id， format 格式, vdf js xml
        # https://api.steampowered.com/ISteamDirectory/GetCMList/v0001/?cellid=0&format=js
        # https://api.steampowered.com/ISteamDirectory/GetCMList/v1/?cellid=148&steamrealm=steamchina
        url = 'https://api.steampowered.com/ISteamDirectory/GetCMListForConnect/v0001/?cellid=0&format=js'
        headers = {
            'user-agent': 'Valve/Steam HTTP Client 1.0',
            'accept-charset': 'ISO-8859-1,utf-8,*;q=0.7',
            'accept': 'text/html,*/*;q=0.9'
        }
        resp = session.get(url, headers=headers)
        resp.raise_for_status()
        resp_json = resp.json()
        cmList = resp_json['response']['serverlist']
        cmList = [server for server in cmList if server['type'] =='websockets' and server['realm'] == 'steamglobal']
        cmList = sorted(cmList, key=lambda x: x["wtd_load"])
        # print(json.dumps(cmList, ensure_ascii=False, indent=2))
        return cmList
    except requests.exceptions.ConnectionError as e:
        print('网络连接异常: ', e)
    except requests.exceptions.Timeout as e:
        print('连接超时: ', e)
    except requests.exceptions.RequestException as e:
        print('请求异常: ', e)
    except requests.exceptions.HTTPError as e:
        print(f'HTTP错误, 状态码: {e.response.status_code}, {e}')
    except ValueError as e:
        print('响应解析异常: ', e)