# -*- coding: utf-8 -*-
# description: 配置
# author:xzh
# create time:2024-10-14
#coding:utf-8

# from enum import Enum
 
class Server():
  IP = "0.0.0.0"
  PORT = 5000

class Log():
  FILENAME = "logs/web_logs"
  LEVEL = "info"

class GPT():
  api_base_url = "https://api.chatanywhere.tech"
  #这里填入你的 key,可以f去https://peiqishop.me/申请免费的测试key
  api_key = ""

class Mysql():
  USERNAME = ''
  PASSWORD = ''
  HOSTNAME = ''
  PORT = 3306
  DATABASE = ''

class Redis():
  REDIS_HOST = '127.0.0.1'
  REDIS_PORT = 6379
  REDIS_PASSWORD = ''
  REDIS_POLL = 10
  REDIS_DB = 2
  REDIS_DECODE_RESPONSES = True

class Wxyy():
  '''
  可以去百试申请
  '''
  app_id = ''
  api_key = ''
  secret_key = ''
