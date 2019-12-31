import subprocess
import time
import paramiko
import select
import redis
import socket
import pymysql
import os
import datetime
import sys
import logging
import logging.handlers
import threading
import multiprocessing
from utils import *
from pymongo import MongoClient

# from config import *
dir_path = os.getcwd()
config_path = dir_path+'/config/config.txt'

conn = MongoClient('127.0.0.1', 27017)
db = conn.monitor_copy
moni_data = db.moni_data
moni_script = db.moni_script

# logging初始化工作
logging.basicConfig()
# myapp的初始化工作
myapp = logging.getLogger('moniserv')
myapp.setLevel(logging.INFO)
# 写入文件，如果文件超过100个Bytes，仅保留5个文件。
handler = logging.handlers.RotatingFileHandler(
    'logs/moni.log', maxBytes=maxBytes, backupCount=backupCount)
logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(logging_format)
myapp.addHandler(handler)

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def run(moni_time):
    while True:
        with open(config_path,'r') as yaml_file:
            yaml_obj = yaml_file.readlines()
        timestamp = int(time.time())
        for dict in yaml_obj:
            dict = eval(dict)
            host = dict['host']
            user = dict['user']
            pwd = dict['pwd']
            # print('------------开始认证......-----------')
            try:
                # client = paramiko.SSHClient()
                # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                #
                # client.connect(host, 22, username=user, password=pwd, timeout=4)
                # # print(dir_path+'/monitor_perf.py')
                # cmd0 = "ps -ef | grep monitor_server.py | grep -v grep | awk '{print $2}' | xargs kill -15"
                # client.exec_command(cmd0)
                client.connect(host, 22, username=user, password=pwd, timeout=4)
                cmd = 'python3 {}'.format(remote_file)
                sdtin, stdout, stderr = client.exec_command(cmd)
                for i, line in enumerate(stdout):
                    dic_data = eval(line)
                    print(dic_data)
                    if dic_data:
                        total_mess = dic_data['total_mess']
                        total_mess['timestamp'] = timestamp
                        pid_list = dic_data['pid_mess']
                        moni_data.insert(total_mess)
                        for pid_ss in pid_list:
                            if pid_ss:
                                pid_ss['timestamp'] = timestamp
                                moni_script.insert(pid_ss)
                # print('result----{}'.format(result))
                # 服务器开启
                client.close()
            except Exception as e:
                # 服务器禁用或者账号密码错误
                # print('------------认证失败!.....-----------')
                print(e)
                myapp.info('error_ip:{}'.format(host))
                myapp.info(e)


        time.sleep(moni_time)
    #     # p = multiprocessing.Process(target=data_run,args=(host,user,pwd,time_))
    #     # p.start()
    #     # p.join()
    #     t = threading.Thread(target=data_run,args=(host,user,pwd,time_))
    #     t.start()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        moni_time = 1800
    else:
        moni_time = str(sys.argv[1])
    run(moni_time)