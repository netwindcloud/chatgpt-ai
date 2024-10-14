# -*- coding: utf-8 -*-
# description: 文心一言API
# author:xzh
# create time:2024-10-12

from config.config import Wxyy,Redis
import requests
import json
import redis
import time
from flask import Blueprint,request,render_template,Response

wxyy = Blueprint("wxyy",__name__)
wxyy.template_folder='../templates'
wxyy.static_folder='../static'

@wxyy.route("/",methods=['GET' , 'POST'])
def index_wxyy():
    return render_template('pc.html',name='wxyy')

@wxyy.route("/chat",methods=['GET' , 'POST'])
def chat():
    app_id =  Wxyy.app_id
    api_key = Wxyy.api_key
    secret_key = Wxyy.secret_key
    prompt = request.args.get('q','')
    print('prompt:'+prompt)
    
    chat = WXYY(app_id,api_key,secret_key)
    ans_content = chat.get_answer(prompt)

    return ans_content

@wxyy.route("/stream",methods=['GET' , 'POST'])
def stream():
    app_id =  Wxyy.app_id
    api_key = Wxyy.api_key
    secret_key = Wxyy.secret_key
    prompt = request.args.get('q','')
    print('prompt:'+prompt)

    chat = WXYY(app_id,api_key,secret_key)
    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
    }
    return Response(chat.get_answer_stream(prompt), mimetype='text/event-stream',headers=headers)

class WXYY:
    """
    文心一言类
    """
    def __init__(self, app_id,api_key,secret_key):
        self.app_id = app_id
        self.api_key = api_key
        self.secret_key = secret_key

    @property
    def wxyy_access_token(self):
        # return "24.3b2acaf700d425aad954fcc320833e99.2592000.1716605145.282335-42118500"

        redis_host = Redis.REDIS_HOST
        redis_port = Redis.REDIS_PORT
        redis_db = Redis.REDIS_DB
        redis_password = Redis.REDIS_PASSWORD

        # print('redis_host:'+redis_host)

        # 连接到Redis实例
        r = redis.Redis(host=redis_host, port=redis_port, db=redis_db,password=redis_password)

        # 检查键是否存在
        if r.exists(self.app_id):
            # 获取键的值
            wxyy_value = r.get(self.app_id).decode('utf-8')
            value_json = json.loads(wxyy_value)

            if int(time.time()) < value_json['expire_time']:
                return value_json['access_token']
            else:
                access_token, expire_time = self.get_access_token()
                r_value = dict()
                r_value['access_token'] = access_token
                r_value['expire_time'] = expire_time

                r.set(self.app_id, json.dumps(r_value))
                print(r_value)
                return access_token
        else:
            access_token, expire_time = self.get_access_token()
            r_value = dict()
            r_value['access_token'] = access_token
            r_value['expire_time'] = expire_time

            r.set(self.app_id, json.dumps(r_value))
            print(r_value)
            return access_token

    def get_access_token(self):
        """
        使用 API Key，Secret Key 获取access_token
        """
        # auth_url = "https://aip.baidubce.com/oauth/2.0/token"
        # resp = requests.get(auth_url, params={"grant_type": "client_credentials", "client_id": self.api_key, 'client_secret': self.secret_key})
        # return resp.json().get("access_token")
    
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ self.api_key }&client_secret={ self.secret_key }"

        payload = json.dumps("")
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.request("POST",url,headers=headers,data=payload)

        # 获取 access_token 和过期时间
        access_token = response.json()['access_token']
        expires_in = response.json()['expires_in']
        expire_time = int(time.time()) + expires_in - 600  # 减去 600 秒，避免出现时间误差
        # 返回 access_token 和过期时间
        return access_token, expire_time

    def get_wenxin_stream(self,prompt):

        source = "&sourceVer=0.0.1&source=app_center&appName=streamDemo"
        base_url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions"
        url = base_url + "?access_token=" + self.wxyy_access_token + source

        payload = json.dumps({
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            # "temperature": 0.95,
            # "top_p": 0.8,
            # "penalty_score": 1,
            # "disable_search": False,
            # "enable_citation": False,
            # "response_format": "text",
            "stream": True
        })
        headers = {
            'Content-Type': 'application/json'
        }

        return requests.post(url, headers=headers, data=payload, stream=True)

    def get_answer_stream(self,prompt):
        response = self.get_wenxin_stream(prompt)
        for chunk in response.iter_lines():
            chunk = chunk.decode("utf8")
            # print('before:',chunk)
            if chunk[:5] == "data:":
                chunk = chunk[5:]
                chunk = json.loads(chunk)

                chunk = chunk['result']
                chunk = chunk.replace('\n', '<br>')
                chunk = f'data: { chunk }\n\n'
                print(chunk)
                yield chunk
            # time.sleep(0.01)
           
        yield f'data:{"[done]"}\n\n'  # 结束标志输入到浏览器
