import os
import json
import re
import copy
from os import popen
import random

server_confi_path = '/Users/liusen/Documents/myGit/LaMer/config/config.txt'
total_servers_path = 'total_servers.json'
# total_servers_path = '/Users/liusen/Documents/myGit/LaMer/config/total_servers.json'
database_dir_path = '/home/user/Database'
filter_names_global = ['B', 'Priv']


def generate_database_json(path='数据集.xlsx'):

    num = 0
    # 名称
    # 任务
    # 发布机构
    # 发布时间
    # 官方网址
    # 数量
    # 备注
    dic_key = ['name', 'tesk', 'issuer', 'publish_timestamp', 'website', 'count', 'remarks']
    result_arr = list()
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_index(0)  # 根据顺序获取sheet
    for row in sheet.get_rows():
        dic = {}
        for row_index in range(len(row)):
            # print(row[row_index].value)
            if num == 0:
                # print(row[row_index].value)
                pass
                # dic_key.append(row[row_index].value)
            else:
                dic[dic_key[row_index]] = row[row_index].value
                # setattr(dic, dic_key[row_index], row[row_index].value)
        if num != 0 and num != 1:
            result_arr.append(dic)
        num += 1
    return result_arr


def generate_servers_database_json():
    resutl = generate_database_json()
    for_len = len(resutl)
    with open(server_confi_path, 'r') as conf:
        conf_obj = conf.readlines()
    json_dic = {}
    for i in conf_obj:
        dic_ = eval(i)
        ip = dic_['host']
        shuffle_len = random.choice(range(for_len))
        shuffle_list = copy.deepcopy(resutl)
        random.shuffle(shuffle_list)
        # print(shuffle_len)
        # print(shuffle_list)
        if shuffle_len:
            json_dic[ip] = shuffle_list[:shuffle_len]
        else:
            json_dic[ip] = shuffle_list[shuffle_len]

    with open('server_mode_database.json', 'w') as f:
        json.dump(json_dic, f, ensure_ascii=False, indent=4)


def generate_database_server_json():
    with open('server_mode_database.json', 'r') as f:
        server_data_list = json.load(f)
    data_name_list = []
    for key, value in server_data_list.items():
        for item in value:
            if item['name'] not in data_name_list:
                data_name_list.append(item['name'])
    print(data_name_list)
    data_name_list_copy = copy.deepcopy(data_name_list)
    data_mode_arr = []
    data_mode_dic = {}
    for key, value in server_data_list.items():
        for item in value:
            if item['name'] in data_name_list:
                item['server'] = []
                data_mode_dic[item['name']] = item
                data_name_list.remove(item['name'])
            if item['name'] in data_name_list_copy:
                data_mode_dic[item['name']]['server'].append(key)

    for ket, value in data_mode_dic.items():
        data_mode_arr.append(value)

    with open('data_mode_database.json', 'w') as f:
        json.dump(data_mode_arr, f, ensure_ascii=False, indent=4)


def get_dirpath_from_dirs(file_path, *filter_names):
    file_list = []
    filter_names = list(filter_names)

    filter_paths = []
    filelist = os.listdir(file_path)
    filelist = list(filter(lambda x: x.find('.') == -1, filelist))
    for f in filelist:
        if f in filter_names:
            sub_file_path = os.path.join(file_path, f)
            if os.path.isdir(sub_file_path):
                filter_paths.append(sub_file_path)
                continue
        sub_file_path = os.path.join(file_path, f)
        if os.path.isdir(sub_file_path):
            file_list.append(sub_file_path)
        # 不循环递归向下检测
        # elif os.path.isfile(sub_file_path):
        # 	file_list += get_filepath_from_dirs(sub_file_path)
    return file_list, filter_paths


def get_all_filepath_from_dirs(file_path):
    file_list = []
    filelist = os.listdir(file_path)
    for f in filelist:
        sub_file_path = os.path.join(file_path, f)
        if os.path.isfile(sub_file_path):
            file_list.append(sub_file_path)
        # 循环递归向下检测
        elif os.path.isdir(sub_file_path):
            file_list += get_all_filepath_from_dirs(sub_file_path)
    return file_list


def generate_total_servers_database_json():
    host_arr = ['192.168.88.191', '192.168.88.109']
    json_server_data_arr = []
    for host in host_arr:
        result = get_dirpath_from_dirs('/Users/liusen/Documents/JavaScript/react-demo/priv_cloud/docs/文档')
        '''
        group_server_{}  用于 server 分组
        '''

        def filter_json(path):
            file_name = os.path.basename(path) + "_Info.json"
            file_path = os.path.join(path, file_name)
            return os.path.exists(file_path)

        result = list(filter(filter_json, result))
        group_server_len = len(result)
        json_data = {}
        table_data_json_arr = []
        group_server_index = 0
        for path_index, path in enumerate(result):
            file_name = os.path.basename(path) + "_Info.json"
            file_path = os.path.join(path, file_name)
            with open(file_path, 'r') as f:
                json_ori = json.load(f)
                for key, value in json_ori.items():
                    '''
                    "cifar": [{},{}]
                    group_{} 用于大数据集分组
                    '''
                    item_len = len(value)
                    for i in range(item_len):
                        value[i]['group_index'] = i
                        value[i]['group_len'] = item_len
                        value[i]['group_name'] = key
                        value[i]['group_server_index'] = group_server_index
                        value[i]['group_server_len'] = group_server_len * item_len
                        value[i]['group_server_name'] = host
                        # print(value[i])
                        table_data_json_arr.append(value[i])
                        group_server_index += 1
        json_server_data_arr.extend(table_data_json_arr)
    with open(total_servers_path, 'w') as f_:
        json.dump(json_server_data_arr, f_, ensure_ascii=False, indent=4)


'''
    第一层是 匹配数组
    第二层是 模板数组
'''
def match_arrs(template, target):
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
    host_arr = ['192.168.88.191', '192.168.88.109']
    '''
    做匹配的模板数组
    '''
    test_arr = []
    json_server_data_arr = []
    dir_path = database_dir_path
    for host_index, host in enumerate(host_arr):
        # if host_index == 0:
        #     dir_path = database_dir_path
        # else:
        #     dir_path = database_dir_path_test
        print(dir_path)
        result = get_dirpath_from_dirs(dir_path)
        '''
        group_server_{}  用于 server 分组
        过滤不存在 json 的文件夹
        '''
        def filter_json(path):
            file_name = os.path.basename(path) + "_Info.json"
            file_path = os.path.join(path, file_name)
            return os.path.exists(file_path)

        result = list(filter(filter_json, result))

        group_server_len = len(result)
        json_data = {}
        table_data_json_arr = []
        group_server_index = 0
        for path_index, path in enumerate(result):
            file_name = os.path.basename(path) + "_Info.json"
            file_path = os.path.join(path, file_name)
            if not os.path.exists(file_path):
                print(file_path + " 不存在")
                break
            with open(file_path, 'r') as f:
                json_ori = json.load(f)
                for key, value in json_ori.items():
                    '''
                    "cifar": [{},{}]
                    group_{} 用于大数据集分组
                    '''
                    item_len = len(value)
                    for i in range(item_len):
                        value[i]['group_index'] = i
                        value[i]['group_len'] = item_len
                        value[i]['group_name'] = key
                        value[i]['group_server_index'] = group_server_index
                        value[i]['group_server_len'] = group_server_len * item_len
                        value[i]['group_server_name'] = [host]
                        # print(value[i])
                        table_data_json_arr.append(value[i])
                        group_server_index += 1
        if host_index == 0:
            json_server_data_arr = table_data_json_arr
        else:
            '''
                第一层是 匹配数组
                第二层是 模板数组
            '''
            json_server_data_arr = match_arrs(json_server_data_arr, table_data_json_arr)

    with open(total_servers_path, 'w') as f:
        json.dump(json_server_data_arr, f, ensure_ascii=False, indent=4)


def generate_local_database_server_json():
    '''
    做匹配的模板数组
    '''

    dir_path = database_dir_path
    result, result_filter = get_dirpath_from_dirs(dir_path, *filter_names_global)
    # print(result_filter)
    for item in result_filter:
        data_path, _ = get_dirpath_from_dirs(item)
        if len(data_path):
            result.extend(data_path)
    # print(result)
    # print('****')
    '''
    group_server_{}  用于 server 分组
    过滤不存在 json 的文件夹
    '''
    def filter_json(path):
        file_name = os.path.basename(path) + "_Info.json"
        file_path = os.path.join(path, file_name)
        return os.path.exists(file_path)

    result = list(filter(filter_json, result))
    group_server_len = len(result)

    table_data_json_arr = []
    group_server_index = 0
    for path_index, path in enumerate(result):
        file_name = os.path.basename(path) + "_Info.json"
        file_path = os.path.join(path, file_name)
        if not os.path.exists(file_path):
            # print(file_path + " 不存在")
            break
        with open(file_path, 'r') as f:
            json_ori = json.load(f)
            for key, value in json_ori.items():
                '''
                "cifar": [{},{}]
                group_{} 用于大数据集分组
                '''
                item_len = len(value)
                for i in range(item_len):
                    value[i]['group_index'] = i
                    value[i]['group_len'] = item_len
                    value[i]['group_name'] = key
                    value[i]['group_server_index'] = group_server_index
                    value[i]['group_server_len'] = group_server_len * item_len
                    # print(value[i])
                    table_data_json_arr.append(value[i])
                    group_server_index += 1
    return table_data_json_arr


if __name__ == "__main__":
    # generate_servers_database_json()
    # generate_database_server_json()
    # generate_total_database_server_json()
    local_json = generate_local_database_server_json()
    print(json.dumps(local_json))



