# -*- coding: utf-8 -*-
# description: mysql 数据库访问类pip 
# author:xzh
# create time:2024-10-14

import mysql.connector
import traceback
from config.config import Mysql


class MySql(object):
  '''
  类初始化时设定必要的参数
  '''
  def __init__(self, host: str,port:str, dbname: str, username: str, password: str, debug=True):
    self.debug = debug
    self.host = host
    self.port = port
    self.dbname = dbname
    self.username = username
    self.password = password

  def __del__(self):
    pass

  def __fetchall__(self, sql):
    if self.debug:
      print('execute sql : %s' % sql)
    results = None
    db = None

    try:
      db = self.__get_connect__()
      cursor = db.cursor()
      cursor.execute(sql)
      results = cursor.fetchall()
    except Exception as error:
      traceback.print_exc()
    finally:
      cursor.close()
      db.close()
    return results


  def __fetchone__(self, sql):
    if self.debug:
      print('execute sql : %s' % sql)
    result = None
    db = None
    try:
      db = self.__get_connect__()
      cursor = db.cursor()
      cursor.execute(sql)
      result = cursor.fetchone()
    except Exception as error:
      traceback.print_exc()
    finally:
      cursor.close()
      db.close()
    return result


  def __execute_sql__(self, sql):
    if self.debug:
      print('execute sql : %s' % sql)
    result = None
    db = None
    try:
      db = self.__get_connect__()
      cursor = db.cursor()
      result = cursor.execute(sql)
      db.commit()
    except Exception as error:
      traceback.print_exc()
      db.rollback()
    finally:
      cursor.close()
      db.close()
    return result

  def __get_connect__(self):
    return mysql.connector.connect(
      host=self.host,
      port=self.port,
      username=self.username,
      password=self.password,
      database=self.dbname
    )

global mysql_helper
mysql_helper = MySql(Mysql.HOSTNAME,Mysql.PORT,Mysql.DATABASE,Mysql.USERNAME,Mysql.PASSWORD)

if __name__ == "__main__":
  pass
