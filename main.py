# -*- coding: utf-8 -*-
# description: 主程序入口
# author:xzh
# create time:2024-10-14


from flask import Flask,render_template,redirect,request
import os
from config.config import Server,GPT

app = Flask(__name__)
app.static_folder='./static'
app.template_folder='./templates'

# 注册蓝图
from gpt.gpt import ChatGPT, gpt
app.register_blueprint(gpt,url_prefix='/gpt')

from wxyy.wxyy import wxyy
app.register_blueprint(wxyy,url_prefix='/wxyy')

#设置secret key
app.config['SECRET_KEY'] = os.urandom(24)


@app.route('/')
def default():
  # return "abcdefg"
  ip = request.remote_addr
  user_agent = request.user_agent
  # print(user_agent)
  return render_template('pc.html')

@app.route('/index')
def index():
  return 'this is a apollo ai chat application'

@app.route('/chat',methods=['GET' , 'POST'])
def chat():
  prompt = request.args.get('q','')
  model = request.args.get('m','')
  url = '/gpt/chat?m='+model+'&q='+prompt
  return redirect(url)

@app.route('/img',methods=['GET' , 'POST'])
def img():
  prompt = request.args.get('q','')
  prompt = prompt.replace('\n',' ')
  model = request.args.get('m','')
  url = '/gpt/img?m='+model+'&q='+prompt
  return redirect(url)


if __name__ == '__main__':
  app.debug = True
  app.run(host = Server.IP, port = Server.PORT)
