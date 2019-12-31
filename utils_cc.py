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
config_path = dir_path+'/config/config_cc.txt'
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
                mo_da = moni_data(net_num=total_mess['net_num'], gpu_info=total_mess['gpu_info'],
                                  cpuUsagePercent=total_mess['cpuUsagePercent'], net_ip=total_mess['net_ip'],
                                  diskUsage=total_mess['diskUsage'], TotalMemory=total_mess['TotalMemory'],
                                  cpu_model=total_mess['cpu_model'], timestamp=total_mess['timestamp'],
                                  UsageMemory=total_mess['UsageMemory'], diskTotal=total_mess['diskTotal'],
                                  cpu_num=total_mess['cpu_num'])
                mo_da.save()
                for pid_ss in pid_list:
                    if pid_ss:
                        pid_ss['timestamp'] = timestamp
                        mo_sc = moni_script(gpu_mem=pid_ss['gpu_mem'], duration=pid_ss['duration'],
                                            user=pid_ss['user'], gpu_pid=pid_ss['gpu_pid'],
                                            start_time=pid_ss['start_time']
                                            , config=pid_ss['config'], gpu_use=pid_ss['gpu_use'],
                                            net_ip=pid_ss['net_ip'], timestamp=pid_ss['timestamp'])
                        mo_sc.save()

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
                mo_da = moni_data(net_num=total_mess['net_num'], gpu_info=total_mess['gpu_info'],
                                  cpuUsagePercent=total_mess['cpuUsagePercent'], net_ip=total_mess['net_ip'],
                                  diskUsage=total_mess['diskUsage'], TotalMemory=total_mess['TotalMemory'],
                                  cpu_model=total_mess['cpu_model'], timestamp=total_mess['timestamp'],
                                  UsageMemory=total_mess['UsageMemory'], diskTotal=total_mess['diskTotal'],
                                  cpu_num=total_mess['cpu_num'])
                mo_da.save()
                for pid_ss in pid_list:
                    if pid_ss:
                        pid_ss['timestamp'] = timestamp
                        mo_sc = moni_script(gpu_mem=pid_ss['gpu_mem'], duration=pid_ss['duration'],
                                            user=pid_ss['user'], gpu_pid=pid_ss['gpu_pid'],
                                            start_time=pid_ss['start_time']
                                            , config=pid_ss['config'], gpu_use=pid_ss['gpu_use'],
                                            net_ip=pid_ss['net_ip'], timestamp=pid_ss['timestamp'])
                        mo_sc.save()

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

def ces(moni_data,moni_script):
    timestamp = int(time.time())
    data = {'total_mess': {'net_num': 2, 'cpu_num': 40, 'cpu_model': 'Intel(R) Xeon(R) CPU E5-2630 v4 @ 2.20GHz', 'UsageMemory': 65, 'net_ip': '192.168.88.60', 'cpuUsagePercent': 1603.9, 'diskUsage': 16, 'gpu_info': [{'name': 'TITAN Xp', 'script': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6239, 'start_time': '12月26', 'duration': '1282:10', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38841', 'gpu_use': 0}], 'usedMemry': 6552551424, 'power': '167W/250W', 'percent': 51.2, 'version': '10.410.48', 'totalMemry': 12788498432, 'temp': 70, 'fan': 0}, {'name': 'TITAN Xp', 'script': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6231, 'start_time': '12月26', 'duration': '1298:46', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38842', 'gpu_use': 1}], 'usedMemry': 6544162816, 'power': '81W/250W', 'percent': 51.2, 'version': '10.410.48', 'totalMemry': 12788498432, 'temp': 76, 'fan': 1}, {'name': 'TITAN Xp', 'script': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6215, 'start_time': '12月26', 'duration': '1300:06', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38843', 'gpu_use': 2}], 'usedMemry': 6527385600, 'power': '82W/250W', 'percent': 51.0, 'version': '10.410.48', 'totalMemry': 12788498432, 'temp': 72, 'fan': 2}, {'name': 'TITAN Xp', 'script': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6249, 'start_time': '12月26', 'duration': '1288:01', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38844', 'gpu_use': 3}], 'usedMemry': 6563037184, 'power': '75W/250W', 'percent': 51.3, 'version': '10.410.48', 'totalMemry': 12788498432, 'temp': 71, 'fan': 3}, {'name': 'TITAN Xp', 'script': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6273, 'start_time': '12月26', 'duration': '1338:47', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38845', 'gpu_use': 4}], 'usedMemry': 6588203008, 'power': '78W/250W', 'percent': 51.5, 'version': '10.410.48', 'totalMemry': 12788498432, 'temp': 67, 'fan': 4}, {'name': 'TITAN Xp', 'script': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6295, 'start_time': '12月26', 'duration': '1327:02', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38846', 'gpu_use': 5}], 'usedMemry': 6611271680, 'power': '86W/250W', 'percent': 51.7, 'version': '10.410.48', 'totalMemry': 12788498432, 'temp': 73, 'fan': 5}, {'name': 'TITAN Xp', 'script': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6457, 'start_time': '12月26', 'duration': '1296:23', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38847', 'gpu_use': 6}], 'usedMemry': 6781140992, 'power': '283W/250W', 'percent': 53.0, 'version': '10.410.48', 'totalMemry': 12788498432, 'temp': 72, 'fan': 6}, {'name': 'TITAN Xp', 'script': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6171, 'start_time': '12月26', 'duration': '1301:57', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38848', 'gpu_use': 7}], 'usedMemry': 6481248256, 'power': '139W/250W', 'percent': 50.7, 'version': '10.410.48', 'totalMemry': 12788498432, 'temp': 72, 'fan': 7}], 'TotalMemory': 125, 'diskTotal': 439}, 'pid_mess': [{'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6239, 'start_time': '12月26', 'duration': '1282:10', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38841', 'gpu_use': 0}, {'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6231, 'start_time': '12月26', 'duration': '1298:46', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38842', 'gpu_use': 1}, {'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6215, 'start_time': '12月26', 'duration': '1300:06', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38843', 'gpu_use': 2}, {'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6249, 'start_time': '12月26', 'duration': '1288:01', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38844', 'gpu_use': 3}, {'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6273, 'start_time': '12月26', 'duration': '1338:47', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38845', 'gpu_use': 4}, {'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6295, 'start_time': '12月26', 'duration': '1327:02', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38846', 'gpu_use': 5}, {'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6457, 'start_time': '12月26', 'duration': '1296:23', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38847', 'gpu_use': 6}, {'config': '/home/user/workspace/zb/workspace-grid_rcnn/grid_cascade_mapping/Pet-dev/cfgs/rcnn/mscoco/grid_cascade/bretter_roi/e2e_grid_cascade@56_rcnn_R-50-FPN-600_0.5x.yaml', 'gpu_mem': 6171, 'start_time': '12月26', 'duration': '1301:57', 'user': 'user', 'net_ip': '192.168.88.60', 'gpu_pid': '38848', 'gpu_use': 7}]}
    datat = data['total_mess']
    pid_lis = data['pid_mess']
    datat['timestamp'] = timestamp
    mo_da = moni_data(net_num=datat['net_num'],gpu_info=datat['gpu_info'],cpuUsagePercent=datat['cpuUsagePercent'],net_ip=datat['net_ip'],diskUsage=datat['diskUsage'],TotalMemory=datat['TotalMemory'],
                    cpu_model=datat['cpu_model'],timestamp=datat['timestamp'],UsageMemory=datat['UsageMemory'],diskTotal=datat['diskTotal'],cpu_num=datat['cpu_num'])
    mo_da.save()
    for pid_dic in pid_lis:
        if pid_dic:
            pid_dic['timestamp'] = timestamp
            mo_sc = moni_script(gpu_mem=pid_dic['gpu_mem'],duration=pid_dic['duration'],user=pid_dic['user'],gpu_pid=pid_dic['gpu_pid'],start_time=pid_dic['start_time']
                                ,config=pid_dic['config'],gpu_use=pid_dic['gpu_use'],net_ip=pid_dic['net_ip'],timestamp=pid_dic['timestamp'])
            mo_sc.save()

if __name__ == '__main__':

    teee()