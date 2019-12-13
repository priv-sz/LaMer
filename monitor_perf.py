import os
import psutil
import uuid
import json
import time
import re

from os import popen
from pynvml import *
from psutil import net_if_addrs

def get_netcard():
    netcard_info = []
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[0] == 2 and not item[1] == '127.0.0.1' and '192.168.88.' in item[1]:
                netcard_info.append((k, item[1]))
    return netcard_info

# 获取gpu对应pid信息
def ndivi_pid(gpu_num):
    cmd = 'nvidia-smi'
    result_str = popen(cmd).read()
    result_arr = []
    for i, item in enumerate(result_str.split('\n')):
        if ('GPU' in item and 'PID' in item):
            result_arr = result_str.split('\n')[i + 2:-2]
            continue
    pid_list = []
    for i in result_arr:
        pid_dic = {}
        res = i.split()
        # print(res)
        if res[2].isdigit():
            if int(res[1]) == gpu_num and res[3]=='C':
                pid_dic['gpu_use'] = int(res[1])
                pid_dic['gpu_pid'] = res[2]
                pid_dic['gpu_mem'] = int(res[5].split('M')[0])
                cmd = 'ps aux|grep -v grep | grep {}'.format(res[2])
                result_str = popen(cmd).read()
                asd = re.sub(' +', ' ', result_str)
                ress = asd.split(' ')
                # print(ress)
                pid_dic['user'] = ress[0]
                pid_dic['config'] = ress[-1].split('\n')[0]
                pid_dic['duration'] = ress[9]
                pid_dic['start_time'] = ress[8]
                pid_list.append(pid_dic)
        # cmd = 'ps -ef | grep {} | grep -v grep'.format(res[2])

    return pid_list


# 获取gpu显存、型号和温度
def gpu_total(gpu_num,net_ip):
    gpu_list = []
    pid_mess = []

    for i in range(gpu_num):
        gpu_dict = {}
        timestamp = int(time.time())
        handle = nvmlDeviceGetHandleByIndex(i)
        # 获取型号
        device_model = nvmlDeviceGetName(handle).decode()
        # 获取温度
        temperat_model = nvmlDeviceGetTemperature(handle,0)
        meminfo = nvmlDeviceGetMemoryInfo(handle)
        # 功率
        molecular = str(int(nvmlDeviceGetPowerUsage(handle)/1024))
        denominator = str(int(nvmlDeviceGetEnforcedPowerLimit(handle)/1000))
        gpu_version = nvmlSystemGetNVMLVersion().decode()
        power = molecular+"W"+"/"+denominator+"W"
        meminfo_ = meminfo.used
        meminfo_t = meminfo.total
        # gpu百分比获取
        meminofo_num = (meminfo_ / meminfo_t) * 100
        gpu_dict['name'] = device_model
        gpu_dict['totalMemry'] = meminfo_t
        gpu_dict['usedMemry'] = meminfo_
        gpu_dict['temp'] = temperat_model
        gpu_dict['fan'] = i
        gpu_dict['power'] = power
        gpu_dict['percent'] = round(meminofo_num,1)
        gpu_dict['script'] = ndivi_pid(i)
        gpu_dict['version'] = gpu_version
        # print(gpu_dict['script'])
        for i in gpu_dict['script']:
            i['net_ip'] = net_ip
            i['timestamp'] = timestamp
            pid_mess.append(i)
        gpu_list.append(gpu_dict)

    # gpuUsagePercent = sum(gpu_list)
    return gpu_list,pid_mess
def network_num():
    num = 0
    for k, v in net_if_addrs().items():
        if k.startswith('eth'):
            num += 1
    return num

# 获取cpu型号、核数
def getCpu():
    num = 0
    with open('/proc/cpuinfo') as fd:
        for line in fd:
            if line.startswith('processor'):
                num += 1
            if line.startswith('model name'):
                cpu_model = line.split(':')[1].strip().split()
                cpu_model = ' '.join(cpu_model)
                # cpu_model = cpu_model[0] + ' ' + cpu_model[2] + ' ' + cpu_model[-1]
    return {'cpu_num': num, 'cpu_model': cpu_model}

# 获取ip地址

def base_config():

    nvmlInit()
    now_time = time.time()
    # addr_num = hex(uuid.getnode())[2:]
    # mac地址
    # deviceMac = "-".join(addr_num[i: i + 2] for i in range(0, len(addr_num), 2))
    # cpu占用


    # gpu个数
    gpu_number = nvmlDeviceGetCount()

    # ip地址
    net_name, net_ip = get_netcard()[0]
    # gpu总占用，型号，温度
    # gpuUsagePercent,gpu_model,gpu_temperat = gpu_total(gpu_number)
    gpu_mess,pid_mess = gpu_total(gpu_number,net_ip)
    # print(gpu_mess)
    # 网卡数量
    net_num = network_num()

    # 网关子网掩码
    # routingGateway,routingIPNetmask = net_message()
    # 内存总大小 和占用
    mem = psutil.virtual_memory()
    memtotal = int((mem.total)/1024/1024/1024)
    memused = int((mem.used)/1024/1024/1024)

    # 存储总大小 存储占用
    storage = psutil.disk_usage('/')
    storagetotal = int((storage.total)/1024/1024/1024)
    storageused = int((storage.used)/1024/1024/1024)
    # (status, output) = subprocess.getstatusoutput(
    #     "nvidia-smi -q -i %s -d TEMPERATURE| grep 'GPU Current Temp' | cut -d' ' -f 24".format('1'))
    # TODO 新增内容
    # cpu型号
    cpu_model = getCpu()['cpu_model']
    # cpu核数
    cpu_num = getCpu()['cpu_num']
    cpuUsage_list = psutil.cpu_percent(percpu=True)
    cpuUsagePercent = round(sum(cpuUsage_list),1)
    # gpu版本

    # 暂不能用
    # 操作系统名称
    # sysname = os.uname().sysname
    # release = os.uname().release
    # system_name = sysname+'-'+release
    # 获取系统版本
    # system_ver = os.uname().version
    # 操作系统类型
    # system_type = os.uname().machine

    # gpu型号  gpu_model
    # gpu温度  gpu_temperat


    dic_data = {'total_mess':{
        # 'deviceMac':deviceMac,
        'cpuUsagePercent':cpuUsagePercent,
        # 'gpuUsagePercent':gpuUsagePercent,
        'net_num':net_num,
        'gpu_info':gpu_mess,
        'TotalMemory':memtotal,
        'UsageMemory':memused,
        'diskTotal':storagetotal,
        'diskUsage':storageused,
        'cpu_model':cpu_model,
        'cpu_num':cpu_num,
        # 'gpu_version':gpu_version,
        # 'gpu_model':gpu_model,
        # 'gpu_temperat':gpu_temperat,
        # 'routingGateway':routingGateway,
        # 'routingIPNetmask':routingIPNetmask,
        'net_ip':net_ip,
        'timestamp':int(now_time)
        # 'system_name':system_name,
        # 'system_ver':system_ver,
        # 'system_digits':system_digits,
        # 'system_type':system_type

    },'pid_mess':pid_mess}
    return dic_data
    # return dic_data

# def run(moni_time):
#     while True:
#
#         dic_data = base_config()
#         print(dic_data)
#         total_mess = dic_data['total_mess']
#         pid_list = dic_data['pid_mess']
#
#         moni_data.insert(total_mess)
#
#         for pid_ss in pid_list:
#             if pid_ss:
#                 timestamp = time.time()
#                 pid_ss['net_ip'] = total_mess['net_ip']
#                 pid_ss['timestamp'] = int(timestamp)
#                 moni_script.insert(pid_ss)
#         time.sleep(moni_time)


if __name__ == '__main__':
    print(base_config())