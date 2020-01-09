import paramiko
import os
import sys
import copy
import json
from os import popen
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
python_script = '/home/user/Monitor_script/generate_database_json.py'
# server_confi = BASE_DIR + '/scripts/config.txt'
server_confi = BASE_DIR + '/config/config.txt'
target_json = BASE_DIR + '/config/total_servers.json'


def match_arrs(template, target):
    '''
    第一层是 匹配数组
    第二层是 模板数组
    '''
    for table_data_json_arr_index, table_data_json_arr_item in enumerate(target):
        match_flag = False
        for json_template_arr_index, json_template_item in enumerate(template):
            print('{}--{}'.format(table_data_json_arr_index, json_template_arr_index))
            if json_template_item['name'] == table_data_json_arr_item['name']:
                match_flag = True
                json_template_item['group_server_name'].extend(table_data_json_arr_item['group_server_name'])
                break
        if not match_flag:
            # print(table_data_json_arr_item)
            template.append(table_data_json_arr_item)

    return template


def generate_total_database_server_json():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    with open(server_confi, 'r') as f:
        conf = f.readlines()
    conf = list(map(lambda x: eval(x), conf))
    json_server_data_arr = []
    for host_index, dics in enumerate(conf):
        try:
            host = dics['host']
            user = dics['user']
            pwd = dics['pwd']

            client.connect(host, 22, username=user, password=pwd, timeout=3)
            cmd = 'ls {}'.format(python_script)
            sdtin, stdout, stderr = client.exec_command(cmd)
            if stdout.readline() != '':
                print("exist")
                print(host)
                cmd = 'python3 {}'.format(python_script)
                sdtin, stdout, stderr = client.exec_command(cmd)

                def join_host(item):
                    item['group_server_name'] = [host]
                    return item

                for i, line in enumerate(stdout):
                    table_data_json_arr = eval(line)
                    # 添加 group_server_name
                    table_data_json_arr = list(map(join_host, table_data_json_arr))

                if host_index == 0:
                    json_server_data_arr = table_data_json_arr
                else:
                    '''
                        第一层是 匹配数组
                        第二层是 模板数组
                    '''
                    json_server_data_arr = match_arrs(json_server_data_arr, table_data_json_arr)

            else:
                print("not exist")
                continue
        except Exception as e:
            print('***********')
            print(host)
            print(e)
            traceback.print_exc()
            print('***********')

    with open(target_json, 'w') as f:
        json.dump(json_server_data_arr, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    generate_total_database_server_json()