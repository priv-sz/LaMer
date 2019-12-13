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
from pymongo import MongoClient

# from config import *
dir_path = os.getcwd()
config_path = dir_path+'/config/config.txt'

def run(ip):

    with open(config_path,'r') as yaml_file:
        yaml_obj = yaml_file.readlines()

    for dict in yaml_obj:
        dict = eval(dict)
        host = dict['host']
        user = dict['user']
        pwd = dict['pwd']
        time_ = dict['time']
        if ip == host:
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                client.connect(host, 22, username=user, password=pwd, timeout=4)
                # print(dir_path+'/monitor_perf.py')
                cmd0 = "ps -ef | grep monitor_perf.py | grep -v grep | awk '{print $2}' | xargs kill -15"
                client.exec_command(cmd0)
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                client.connect(host, 22, username=user, password=pwd, timeout=4)
                cmd = 'python3 /home/user/Program/ws/monitor_web/monitor_perf.py {}'.format(time_)
                client.exec_command(cmd)

                # print('result----{}'.format(result))
                # 服务器开启
                # print('------------认证成功!.....-----------')
            except Exception as e:
                # 服务器禁用或者账号密码错误
                # print('------------认证失败!.....-----------')
                status = 0
                print(e)
                continue

            client.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        host = "192.168.88.91"
    else:
        host = str(sys.argv[1])
    run(host)