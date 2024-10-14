# -*- coding: utf-8 -*-
# description: GPT
# author:xzh
# create time:2024-10-12


from config.config import GPT
import random
import time
from openai import OpenAI
import requests
import json
import os
import time
from PIL import Image,ImageDraw,ImageFont
from flask import Blueprint,request,render_template,Response,send_file


gpt = Blueprint("gpt",__name__)
gpt.template_folder='../templates'
gpt.static_folder='../static'
api_url = GPT.api_base_url 
api_key = GPT.api_key

@gpt.route("/")
def index_gpt():
    ip = request.remote_addr
    user_agent = request.user_agent
    print(str(ip)+':'+str(user_agent))

    chat = ChatGPT(api_url,api_key)
    # chat.get_for_TTS('愿生命如阳光般明亮，努力如璀璨的星，在人生的舞台上，绽放出无限的光芒。')
    return render_template('pc.html',name='gpt')

@gpt.route("/chat",methods=['GET' , 'POST'])
def chat():
    prompt = request.args.get('q','')
    model = request.args.get('m','')

    print('prompt:'+prompt)
    print('model:'+model)
    
    chat = ChatGPT(api_url,api_key)
    headers = {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no',
    }
    if model == 'gpt4':
        return Response(chat.get_ans_for_gpt4(prompt), mimetype='text/event-stream',headers=headers)
    else:
        return Response(chat.get_ans_for_Completions(prompt), mimetype='text/event-stream',headers=headers)

@gpt.route("/img",methods=['GET' , 'POST'])
def img():
    prompt = request.args.get('q','')
    prompt = prompt.replace('\n',' ')
    m = request.args.get('m','')
    s = request.args.get('s','')
    
    chat = ChatGPT(api_url,api_key)
    
    return chat.generations_images(prompt)

@gpt.route('/show',methods=['GET' , 'POST'])
def show_image():
    path = request.args.get('image')
    print('path:'+path)
    # 指定要显示的图片路径
    image_path = 'static/generations/' + os.path.basename(path)
    print ('image_path:'+image_path)
    
    return send_file(image_path, mimetype='image/jpeg')

@gpt.route("/tts",methods=['GET' , 'POST'])
def tts():
    prompt = request.args.get('q','')
    m = request.args.get('m','')
    s = request.args.get('s','')
    
    chat = ChatGPT(api_url,api_key)
    
    return chat.get_for_TTS(prompt)

class ChatGPT:
    """
    ChatGPT类
    """
    def __init__(self,api_url,api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.streamHandler = ''
        self.question = ''
        self.dfa = None
        self.check_sensitive = False

    def get_ans_for_gpt4(self,prompt):
        start_time = time.time() #用于记录响应时间
        client = OpenAI(api_key=self.api_key,base_url=self.api_url+"/v1")
        qus_dict= dict()
        recv_messages=[]
        # qus_dict= {'role':'system','content':'我是太阳神小A，由太阳神公司创造的。是一个智能助手，可以帮助用户解答问题、提供相关信息、执行指令等。我通过人工智能技术实现与用户的交互，帮助用户提高工作效率和提供便利。如有需要，我可以帮助您解答问题或提供相关服务，欢迎向我提问。'}
        # recv_messages.append(qus_dict)

        # send_dict= {'role':'system','content':'广东太阳神集团成立于1988年8月8日，注册资金3.38114亿港币，是以生产和销售保健品、食品及药品为主的大型本土企业集团'}
        # recv_messages.append(send_dict)
        qus_dict={'role':'user','content': prompt}
        recv_messages.append(qus_dict)
        
        response = client.chat.completions.create(
            # model='gpt-3.5-turbo',
            model='gpt-4-0613',
            messages=recv_messages,
            temperature=0.7,
            stream=True
        )
        collected_chunks = []
        collected_messages = []
        for chunk in response:
            chunk_time = time.time() - start_time  # calculate the time delay of the chunk
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk.choices[0].delta.content  # extract the message
            collected_messages.append(chunk_message)  # save the message
            # print(f"Message received {chunk_time:.2f} seconds after request: {chunk_message}")  # print the delay and text
            if chunk_message:
                message=chunk_message.replace('\n', '<br>')
                yield f'data: { message }\n\n'
            else:
                pass
        yield f'data:{"[done]"}\n\n'  # 结束标志输入到浏览器

        print(f"Full response received {chunk_time:.2f} seconds after request")
        collected_messages = [m for m in collected_messages if m is not None]
        full_reply_content = ''.join([m for m in collected_messages])
        print(f"Full conversation received: {full_reply_content}")
        
        return Response(full_reply_content, mimetype='text/event-stream')

    def get_ans_for_Completions(self,prompt):
        start_time = time.time() #用于记录响应时间
        client = OpenAI(api_key=self.api_key,base_url=self.api_url+"/v1")
        qus_dict= dict()
        recv_messages=[]
        qus_dict= {'role':'system','content':'我叫微妙风云，是由熊正浩训练的一个智能助手，可以帮助用户解答问题、提供相关信息、执行指令等。我通过人工智能技术实现与用户的交互，帮助用户提高工作效率和提供便利。如有需要，我可以帮助您解答问题或提供相关服务，欢迎向我提问。'}
        recv_messages.append(qus_dict)

        # send_dict= {'role':'system','content':''}
        # recv_messages.append(send_dict)

        #recv_messages.extend(qus_messages)
        qus_dict={'role':'user','content': prompt}
        recv_messages.append(qus_dict)
        
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            # model='gpt-4-0613',
            messages=recv_messages,
            temperature=0.7,
            stream=True
        )
        collected_chunks = []
        collected_messages = []
        for chunk in response:
            chunk_time = time.time() - start_time  # calculate the time delay of the chunk
            collected_chunks.append(chunk)  # save the event response
            chunk_message = chunk.choices[0].delta.content  # extract the message
            collected_messages.append(chunk_message)  # save the message
            # print(f"Message received {chunk_time:.2f} seconds after request: {chunk_message}")  # print the delay and text
            if chunk_message:
                message=chunk_message.replace('\n', '<br>')
                yield f'data: { message }\n\n'
            else:
                pass
        yield f'data:{"[done]"}\n\n'  # 结束标志输入到浏览器

        print(f"Full response received {chunk_time:.2f} seconds after request")
        collected_messages = [m for m in collected_messages if m is not None]
        full_reply_content = ''.join([m for m in collected_messages])
        print(f"Full conversation received: {full_reply_content}")
        
        return Response(full_reply_content, mimetype='text/event-stream')

    def get_ans_for_post(self,prompt):
        # print (prompt)
        start_time = time.time()
        api = self.api_url + '/v1/chat/completions'
        send_messages=[]

        send_dict= {'role':'system','content':'我叫微妙风云，是由熊正浩训练的一个智能助手，可以帮助用户解答问题、提供相关信息、执行指令等。我通过人工智能技术实现与用户的交互，帮助用户提高工作效率和提供便利。如有需要，我可以帮助您解答问题或提供相关服务，欢迎向我提问。'}
        send_messages.append(send_dict)
        # send_dict= {'role':'system','content':'广东太阳神集团成立于1988年8月8日，注册资金3.38114亿港币，是以生产和销售保健品、食品及药品为主的大型本土企业集团'}
        # send_messages.append(send_dict)

        #recv_messages.extend(qus_messages)
        send_dict={'role':'user','content': prompt}
        send_messages.append(send_dict)
        print(send_messages)

        headers = {
            "Content-Type": "application/json",
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            "Authorization": "Bearer " + self.api_key
        }
        json_data = {
            # "model": "gpt-3.5-turbo-16k-0613",
            # "stream":True,
            "model": "gpt-3.5-turbo",
            "messages": send_messages,
            "temperature": 0.7
        }

        try:
            response = requests.post(url=api, headers=headers, json=json_data,stream=True)
            response.encoding = "utf-8"
        except requests.exceptions.HTTPError as e:
            print(f'HTTP错误, 状态码: {e.response.status_code}, {e}')

        if response.status_code == 200:
            res = json.loads(response.text)
            result=res['choices'][0]['message']['content']
            print(result)
            return result
            # yield f'data:{result}\n\n'
            # yield f'data:{"[done]"}\n\n'
        else:
            print("请求失败，状态码：", response.status_code)
            return 'ai 请求失败'
        
        # return Response('response.text', mimetype='text/event-stream')
        return 'ai 请求失败'
    
    def save_images(self,url):
        image_filename = url.split('?')[0]
        image_filename = image_filename.split('/')[-1]
        image_dir = os.curdir + '/static/downloads'
        image_path = os.path.join(image_dir,image_filename)
        generated_image = requests.get(url).content

        if not os.path.isdir(image_dir):
            os.mkdir(image_dir)


        with open(image_path, "wb") as image_file:
            image_file.write(generated_image) 
        
        print("image_path:"+image_path)
        return self.watermark_Image(image_path)

    def watermark_Image(self,image_path):
        im = Image.open(image_path)
        draw = ImageDraw.Draw(im)
        text = "https://ai.apollo.cn"
        # 设置字体、字体大小等等
        font = ImageFont.truetype('./static/arial.ttf', 23)
        # 添加水印
        draw.text((im.width-210,im.height-35), text, font=font)
        # im.show()
        image_filename= str(random.randint(1000,9999)) + str(int(time.time())) + ".png"
        image_dir = os.curdir + '/static/generations'
        new_path = os.path.join(image_dir,image_filename)
        im.save(new_path)

        print("new_path:"+new_path)
        return new_path

    def generations_images(self,prompt,size="1024x1024"):
        """
        生成图片并保存
        """
        url = self.api_url + "/v1/images/generations"
        payload = json.dumps({
            "prompt": prompt,
            "n": 1,
            "model": "dall-e-3",
            "size": size,
            # "quality":"hd"
            # 生成图像的大小。必须是256x256、512x512、1024x1024、1024x1792
            # 数量只能是1
            # 图片保存服务器上最长2小时
        })
        headers = {
            'Authorization': 'Bearer '+self.api_key,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            print(response.text)
            data = json.loads(response.text)
            image_url = data['data'][0]['url']
            res = self.save_images(image_url)
        except requests.exceptions.HTTPError as e:
            print(f'HTTP错误, 状态码: {e.response.status_code}, {e}')

        return {'imageurl':res}
    
    def get_models(self):
        url = self.api_url + "/v1/models"
        payload = {}
        headers = {
            'Authorization': 'Bearer '+ self.api_key,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            data = json.loads(response.text)
            # print(data['data'][0]['id'])
            for item in data['data']:
                print(str(item['id']))
        except requests.exceptions.HTTPError as e:
            print(f'HTTP错误, 状态码: {e.response.status_code}, {e}')

        return response.text
    
    def get_for_TTS(self,prompt):
        url = self.api_url + "/v1/audio/speech"
        prompt = str(prompt).replace('\n',' ')

        payload = json.dumps({
            "model": "tts-1",
            "input": prompt,
            "voice": "alloy"
        })
        headers = {
            'Authorization': 'Bearer '+ self.api_key,
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)

        return response.status_code
