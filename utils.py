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
import traceback

# from config import *
dir_path = os.getcwd()
config_path = dir_path+'/config/config.txt'
monit_path = dir_path + '/monitor_server.py'
local_file = dir_path + '/remote_files/monitor_perf.py'
file_local_file = dir_path + '/remote_files/requirements.txt'
remote_file = "/home/user/Monitor_script/monitor_perf_cc.py"
remote_re_file = "/home/user/Monitor_script/requirement.txt"
remote_dir = "/home/user/Monitor_script/"
maxBytes = 102400
backupCount = 10

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def edi_data(host,user,pwd,time_,moni_data,moni_script):
    try:
        timestamp = int(time.time())
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(host, 22, username=user, password=pwd, timeout=3)
        cmd = 'python3 {}'.format(remote_file)
        sdtin, stdout, stderr = client.exec_command(cmd)
        list_arr = []
        for i, line in enumerate(stdout):
            dic_data = eval(line)
            if dic_data:
                total_mess = dic_data['total_mess']
                list_arr.append(total_mess)
                pid_list = dic_data['pid_mess']
                total_mess['timestamp'] = timestamp
                moni_data.insert(total_mess)
                for pid_ss in pid_list:
                    if pid_ss:
                        pid_ss['timestamp'] = timestamp
                        moni_script.insert(pid_ss)

        if list_arr:
            list_arr[0].pop('_id')
        return list_arr

    except Exception as e:
        print(e)
        return 0

def add_data(host,user,pwd,time_,moni_data,moni_script):
    global client
    try:
        # with open(config_path,'r') as yaml_file:
        #     yaml_obj = yaml_file.readlines()
        #
        # for dict in yaml_obj:
        #     dict = eval(dict)
        #     host = dict['host']
        #     user = dict['user']
        #     pwd = dict['pwd']
        #     if ip == host:

        timestamp = int(time.time())
        client.connect(host, 22, username=user, password=pwd, timeout=3)
        ssh = paramiko.Transport((host, 22))
        cmd = 'ls {}'.format(remote_dir)
        sdtin, stdout, stderr = client.exec_command(cmd)
        if stdout.readline() != '':
            print("exist")
        else:
            print("not exist")
            cmd = 'mkdir {}'.format(remote_dir)
            client.exec_command(cmd)
        ssh.connect(username=user, password=pwd)
        sftp = paramiko.SFTPClient.from_transport(ssh)
        try:
            sftp.put(local_file, remote_file)
            sftp.put(file_local_file, remote_re_file)
        except Exception as e:
            print(e)
            # sftp.put(local_file, remote_file)
            # sftp.put(remote_re_file, remote_re_file)
            print("从本地： %s 上传到： %s" % (local_file, remote_file))
            return 0
        ssh.close()

        client.connect(host, 22, username=user, password=pwd, timeout=3)
        _, stdout1, stderr1 = client.exec_command(
            'echo priv123 | sudo -S pip3 install -r {} -i https://pypi.tuna.tsinghua.edu.cn/simple'.format(remote_re_file))
        stdout1.read().decode('utf-8')

        cmd = 'python3 {}'.format(remote_file)
        sdtin, stdout, stderr = client.exec_command(cmd)
        list_arr = []
        for i, line in enumerate(stdout):
            dic_data = eval(line)
            if dic_data:
                total_mess = dic_data['total_mess']
                print(total_mess)
                list_arr.append(total_mess)
                pid_list = dic_data['pid_mess']
                total_mess['timestamp'] = timestamp
                moni_data.insert(total_mess)
                print('insert')
                print('******')
                print(total_mess)
                for pid_ss in pid_list:
                    if pid_ss:
                        pid_ss['timestamp'] = timestamp
                        moni_script.insert(pid_ss)

        if list_arr:
            list_arr[0].pop('_id')
        return list_arr

    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')
        return 0

def teee():
    with open(config_path, 'r') as f:
        conf_txt = f.readlines()
    for dics in conf_txt:
        dicc = eval(dics)
        host = dicc['host']
        user = dicc['user']
        pwd = dicc['pwd']

        client.connect(host, 22, username=user, password=pwd, timeout=3)
        cmd = 'ls {}'.format(remote_dir)
        sdtin, stdout, stderr = client.exec_command(cmd)
        if stdout.readline() != '':
            print("exist")
        else:
            print("not exist")
            cmd = 'mkdir {}'.format(remote_dir)
            client.exec_command(cmd)
        ssh = paramiko.Transport((host, 22))
        ssh.connect(username=user, password=pwd)
        sftp = paramiko.SFTPClient.from_transport(ssh)
        try:
            sftp.put(local_file, remote_file)
            sftp.put(file_local_file, remote_re_file)
        except Exception as e:
            print(e)
            print("从本地： %s 上传到： %s" % (local_file, remote_file))
        ssh.close()
if __name__ == '__main__':

    teee()