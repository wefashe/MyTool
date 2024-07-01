import json
import time
import base64
import urllib.parse

def decode_base64(encoded):
    standard_base64 = encoded.replace('-', '+').replace('_', '/')
    padded_base64 = standard_base64 + '=' * (4 - len(standard_base64) % 4)
    decoded_bytes = base64.b64decode(padded_base64)
    decoded_str = decoded_bytes.decode('utf-8')
    return decoded_str


def decode_token(token:str):
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Invalid Token')
    return decode_base64(parts[0]), decode_base64(parts[1])

def get_cookie(token:str):
    header, body = decode_token(token)
    body_obj = json.loads(body)
    cookie_str = urllib.parse.quote(body_obj['sub']+'||'+token)
    return cookie_str
    
if __name__ == '__main__':
    token = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInN0ZWFtIiwgInN1YiI6ICI3NjU2MTE5OTE3NjgzMjExOCIsICJhdWQiOiBbICJjbGllbnQiLCAid2ViIiwgInJlbmV3IiwgImRlcml2ZSIgXSwgImV4cCI6IDE3MjgxNzkxODUsICJuYmYiOiAxNjg4NTk1MzA0LCAiaWF0IjogMTY5NzIzNTMwNCwgImp0aSI6ICIxNDU1XzIzNTBDMUJBX0UwQTA5IiwgIm9hdCI6IDE2OTcyMzUzMDQsICJnZW4iOiAxLCAicGVyIjogMSwgImlwX3N1YmplY3QiOiAiODIuMTEuMTU0LjUwIiwgImlwX2NvbmZpcm1lciI6ICI4Mi4xMS4xNTQuNTAiIH0.GDKSalpYq1c3f9NdPHqwxj3-QY_Jgx8by6GCAy1ftGraOK91b4TdQx9PGADTIc0U00K5JX3-GLsShO5xgXepDw'
    # token = 'eyAidHlwIjogIkpXVCIsICJhbGciOiAiRWREU0EiIH0.eyAiaXNzIjogInN0ZWFtIiwgInN1YiI6ICI3NjU2MTE5OTE3NjgzMjExOCIsICJhdWQiOiBbICJjbGllbnQiLCAid2ViIiwgInJlbmV3IiwgImRlcml2ZSIgXSwgImV4cCI6IDE3MjgxNzkxODUsICJuYmYiOiAxNjg4NTk1MzA0LCAiaWF0IjogMTY5NzIzNTMwNCwgImp0aSI6ICIxNDU1XzIzNTBDMUJBX0UwQTA5IiwgIm9hdCI6IDE2OTcyMzUzMDQsICJnZW4iOiAxLCAicGVyIjogMSwgImlwX3N1YmplY3QiOiAiODIuMTEuMTU0LjUwIiwgImlwX2NvbmZpcm1lciI6ICI4Mi4xMS4xNTQuNTAiIH0.GDKSalpYq1c3f9NdPHqwxj3-QY_Jgx8by6GCAy1ftGraOK91b4TdQx9PGADTIc0U00K5JX3-GLsShO5xgXepDw'
    header, body = decode_token(token)
    print(header)
    body_obj = json.loads(body)

    body_obj["exp"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(body_obj["exp"]))
    body_obj["nbf"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(body_obj["nbf"]))
    body_obj["iat"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(body_obj["iat"]))
    body_obj["oat"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(body_obj["oat"]))
    print(json.dumps(body_obj, ensure_ascii=False, indent=2))

    cookie_str = get_cookie(token)
    print('steamLoginSecure='+cookie_str)