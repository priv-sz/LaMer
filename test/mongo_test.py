from model.Model import *
import os
import json
import traceback
import mongoengine
import time
import datetime
import json
import copy
from functools import reduce
from copy import deepcopy
mongoengine.connect(db='monitor_copy', host='192.168.88.191:27017')
# mongoengine.connect(db='monitor_copy', host='211.103.201.178:27108')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = BASE_DIR + '/config/config.txt'

def add_user(name, pwd, auth=0):
    try:
        pass
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')


def query_all_user():
    try:
        users = Person.objects()
        users = list(map(lambda x: m2d_exclude(x, '_id', "password"), users))
        print(users)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')


def update_user(userName, **args):
    try:
        user = Person.objects(name=userName).first()
        for i in args:
            print("{} -- {}".format(i, args[i]))
            setattr(user, i, args[i])
        user.save()
        print(m2d_exclude(user))
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')


def query_server(ip):
    query_res = Data.objects(net_ip=ip).order_by('-timestamp').first()
    if query_res:
        dic = m2d_exclude(query_res)
        with open('server_test.json', 'w') as f:
            json.dump(dic, f, ensure_ascii=False, indent=4)
        print(dic['timestamp'])
    else:
        print('无 ip = {}'.format(ip))


def float2int(x):
    for key, value in x.items():
        if type(value) == float:
            x[key] = int(value)
    return x


def section_hours_qurty(func):
    now_time = int(time.time())
    timeArray = time.localtime(now_time)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    now_date = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    loop_count = now_date.hour
    print(loop_count)
    result = []
    for i in range(loop_count + 1):
        # 正序
        time_gte = now_date - datetime.timedelta(hours=loop_count - i, minutes=now_date.minute, seconds=now_date.second)
        timestamp_gte = int(time.mktime(time_gte.timetuple()))
        timestamp_lte = timestamp_gte + 3600
        time_lte = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_lte))
        section_result = func(timestamp_lte, timestamp_gte)
        section_result_len = len(section_result)
        if section_result_len:
            gpu_avg = 0
            temp_avg = 0
            percent_avg = 0
            for index, value in enumerate(section_result):
                gpu_avg += value['gpu']
                temp_avg += value['temp']
                percent_avg += value['percent']
            dic = dict(gpu_avg=int(gpu_avg/section_result_len), temp_avg=int(temp_avg/section_result_len),
                       percent_avg=int(percent_avg/section_result_len), server_info=section_result,
                       timestamp=timestamp_gte
                       )
            result.append(dic)
    return result


def section_hours_script_qurty(func):
    now_time = int(time.time())
    timeArray = time.localtime(now_time)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    now_date = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    loop_count = now_date.hour
    print(loop_count)
    result = []
    for i in range(loop_count + 1):
        # 正序
        time_gte = now_date - datetime.timedelta(hours=loop_count - i, minutes=now_date.minute, seconds=now_date.second)
        timestamp_gte = int(time.mktime(time_gte.timetuple()))
        timestamp_lte = timestamp_gte + 3600
        time_lte = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_lte))
        section_result = func(timestamp_lte, timestamp_gte)
        section_result_len = len(section_result)

        result.append(section_result)
    return result


def section_total_hours_script_qurty(func):
    timestamp_gte, timestamp_lte = get_week()
    result = []

    # 正序
    students = Student.objects().all()
    students_all = list(map(lambda x: m2d_exclude(x), students))

    for student in students_all:
        section_result = func(timestamp_lte, timestamp_gte, student)
        # print(section_result)
        result.append(section_result)
    return result


def total_average_data(timestamp_lte, timestamp_gte):
    data_query = Data._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": timestamp_lte, "$gte": timestamp_gte}}},
        {"$sort": {"timestamp": -1}},
        {'$unwind': '$gpu_info'},
        {"$group": {"_id": {
            'net_ip': '$net_ip',
            'fan': '$gpu_info.fan',
        },
                    "gpu": {"$avg": "$gpu_info.usedMemry"},
                    "temp": {"$avg": "$gpu_info.temp"},
                    "percent": {"$avg": "$gpu_info.percent"},
                    'net_ip': {"$first": "$net_ip"}
                    }},
        {"$group": {"_id": {
            'net_ip': '$net_ip',
        },
            "gpu": {"$sum": "$gpu"},
            "temp": {"$avg": "$temp"},
            "percent": {"$avg": "$percent"},
            'net_ip': {"$first": "$net_ip"}
        }
        },
    ]
    )

    aggre_obj = list(data_query)
    for item in aggre_obj:
        item['timestamp'] = timestamp_lte
        item = float2int(item)
        item.pop('_id')

    return aggre_obj


def total_script_average_data(timestamp_lte, timestamp_gte, student):
    # if student['name'] == '朱滨':
    #     print(1)
    stu_gpu_use_arr = []
    for server in student['server']:
        data_query = Script._get_collection().aggregate([
            {"$match": {"timestamp": {"$lte": timestamp_lte, "$gte": timestamp_gte}, "user": server['user'],
                        "net_ip": server['host']}},
            {"$sort": {"timestamp": -1}},
            {"$group": {"_id": {
                'net_ip': '$net_ip',
                'user': '$user'
            },
                "gpu": {"$sum": "$gpu_mem"},
                'net_ip': {"$first": "$net_ip"},
                'user': {"$first": "$user"}
            }},
        ]
        )

        aggre_obj = list(data_query)
        if len(aggre_obj):
            for item in aggre_obj:
                item['timestamp'] = timestamp_lte
                # TODO 统一数据结构, 单位, 这里除以 30分钟, 默认 30 分钟采集, 后续修改应该读取 server 配置, 读取间隔时间
                item['gpu'] = int(item['gpu'] * 1024 / ((timestamp_lte-timestamp_gte) / (30 * 60)))
                item = float2int(item)
                item.pop('_id')
                stu_gpu_use_arr.append(item)

    result_student = None
    if len(stu_gpu_use_arr):
        result_student = deepcopy(stu_gpu_use_arr[0])
        gpu_mem = 0
        for stu_gpu_use in stu_gpu_use_arr:
            gpu_mem += stu_gpu_use['gpu']
        result_student['gpu'] = gpu_mem
        result_student['name'] = student['name']
    else:
        if len(student['server']):
            server = student['server'][0]
            result_student = dict(gpu=0, user=server['user'], net_ip=server['host'],
                                  timestamp=timestamp_lte, name=student['name'])
        else:
            result_student = dict(gpu=0, user='user', net_ip='无',
                                  timestamp=timestamp_lte, name=student['name'])
    return result_student


def total_server_average_data(timestamp_lte, timestamp_gte):
    timestamp_lte = 1578502800
    timestamp_gte = 1578499200
    print(timestamp_lte-timestamp_gte)
    data_query = Data._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": timestamp_lte, "$gte": timestamp_gte}}},
        {"$sort": {"timestamp": -1}},
        {'$unwind': '$gpu_info'},
        {"$group": {"_id": {
            'net_ip': '$net_ip',
            'fan': '$gpu_info.fan',
        },
            "gpu": {"$avg": "$gpu_info.usedMemry"},
            "temp": {"$avg": "$gpu_info.temp"},
            "percent": {"$avg": "$gpu_info.percent"},
            'net_ip': {"$first": "$net_ip"}
        }},
        {"$group": {"_id": {
            'net_ip': '$net_ip',
        },
            "gpu": {"$sum": "$gpu"},
            "temp": {"$avg": "$temp"},
            "percent": {"$avg": "$percent"},
            'net_ip': {"$first": "$net_ip"}
        }
        },
    ]
    )

    aggre_obj = list(data_query)
    for item in aggre_obj:
        item['timestamp'] = timestamp_lte
        item = float2int(item)
        item.pop('_id')
        # TODO 统一数据结构, 单位, 这里除以 30分钟, 默认 30 分钟采集, 后续修改应该读取 server 配置, 读取间隔时间
        # item['gpu'] = int(item['gpu'] / ((timestamp_lte - timestamp_gte) / (30 * 60)))

    return aggre_obj


# 服务器平均总耗显存
def  section_hours_server(func):
    now_time = int(time.time())
    timeArray = time.localtime(now_time)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    now_date = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    loop_count = now_date.hour
    print(loop_count)
    result = []

    # 正序
    time_gte = now_date - datetime.timedelta(hours=loop_count, minutes=now_date.minute, seconds=now_date.second)
    timestamp_gte = int(time.mktime(time_gte.timetuple()))
    timestamp_lte = timestamp_gte + 3600 * (loop_count + 1)
    time_lte = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_lte))

    section_result = func(timestamp_lte, timestamp_gte)
    # print(section_result)

    return section_result


def get_week():
    now_time = int(time.time())
    timeArray = time.localtime(now_time)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    now_date = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    loop_count = now_date.hour
    week_now = now_date.weekday()
    print(loop_count)

    # 正序
    time_gte = now_date - datetime.timedelta(days=week_now, hours=loop_count, minutes=now_date.minute, seconds=now_date.second)
    timestamp_gte = int(time.mktime(time_gte.timetuple()))
    timestamp_lte = timestamp_gte + 3600 * 24 * 7
    time_lte = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_lte))
    return timestamp_gte, timestamp_lte


def get_today_time():
    now_time = int(time.time())
    timeArray = time.localtime(now_time)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    now_date = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    loop_count = now_date.hour
    print(loop_count)

    # 正序
    time_gte = now_date - datetime.timedelta(hours=loop_count, minutes=now_date.minute,
                                             seconds=now_date.second)
    timestamp_gte = int(time.mktime(time_gte.timetuple()))
    timestamp_lte = now_time + 30*60
    time_lte = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_lte))
    return timestamp_gte, timestamp_lte


def query_week_server_hours():
    timestamp_gte, timestamp_lte = get_week()
    data_query = Data._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": timestamp_lte, "$gte": timestamp_gte}}},
        {"$sort": {"timestamp": -1}},
        {'$unwind': '$gpu_info'},
        {"$group": {"_id": {
                            'net_ip': '$net_ip',
                            'timestamp': '$timestamp',
                            },
            "gpu": {"$avg": "$gpu_info.usedMemry"},
            "temp": {"$avg": "$gpu_info.temp"},
            "percent": {"$avg": "$gpu_info.percent"},
            'net_ip': {"$first": "$net_ip"},
            'timestamp': {'$first': '$timestamp'},
            'fan': {'$push': '$gpu_info.fan'}
        }},
        {"$match": {"gpu": {"$gte": 10*1024*1024}}},
    ]
    )

    aggre_obj = list(data_query)
    total_hours = len(aggre_obj) * 0.5
    # print(total_hours)
    hours_percent = total_hours / (24 * 7 * 10)  # 小时 * 天数 * 服务器数量
    # for item in aggre_obj:
    #     item['timestamp'] = timestamp_lte
    #     item = float2int(item)
    #     item.pop('_id')
    #     # TODO 统一数据结构, 单位, 这里除以 30分钟, 默认 30 分钟采集, 后续修改应该读取 server 配置, 读取间隔时间
    #     # item['gpu'] = int(item['gpu'] / ((timestamp_lte - timestamp_gte) / (30 * 60)))

    return total_hours, hours_percent


def now_free_server():
    timestamp_lte = int(time.time())
    timestamp_gte = timestamp_lte - 40 * 60

    data_query = Data._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": timestamp_lte, "$gte": timestamp_gte}}},
        {"$sort": {"timestamp": -1}},
        {'$unwind': '$gpu_info'},
        {"$group": {"_id": {
            'net_ip': '$net_ip',
            'fan': '$gpu_info.fan',
        },
            "gpu": {"$first": "$gpu_info.usedMemry"},
            "temp": {"$avg": "$gpu_info.temp"},
            "percent": {"$avg": "$gpu_info.percent"},
            'net_ip': {"$first": "$net_ip"},
            'timestamp': {'$first': '$timestamp'},
            'fan': {'$first': '$gpu_info.fan'}
        }},
        {"$match": {"gpu": {"$lte": 10 * 1024 * 1024}}},
    ]
    )

    aggre_obj = list(data_query)
    for item in aggre_obj:
        item = float2int(item)
        item.pop('_id')

    result_dic = {}
    for index, obj in enumerate(aggre_obj):
        if obj['net_ip'] not in result_dic:
            obj_tmp = copy.deepcopy(obj)
            obj_tmp['fan'] = []
            obj_tmp['fan'].append(obj['fan'])
            result_dic[obj['net_ip']] = obj_tmp
        else:
            result_dic[obj['net_ip']]['fan'].append(obj['fan'])
    result = []

    for key, value in result_dic.items():
        value['fan'].sort()
        result.append(value)
    return result


def query_each_server_hours():
    timestamp_gte, timestamp_lte = get_week()
    data_query = Data._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": timestamp_lte, "$gte": timestamp_gte}}},
        {"$sort": {"timestamp": -1}},
        {'$unwind': '$gpu_info'},
        {"$group": {"_id": {
            'net_ip': '$net_ip',
            'timestamp': '$timestamp',
        },
            "gpu": {"$avg": "$gpu_info.usedMemry"},
            "temp": {"$avg": "$gpu_info.temp"},
            "percent": {"$avg": "$gpu_info.percent"},
            'net_ip': {"$first": "$net_ip"},
            'timestamp': {'$first': '$timestamp'}
            # 'timestamp': {'$push': '$timestamp'}
        }},
        {"$match": {"gpu": {"$gte": 10*1024*1024}}},
        {"$group": {"_id": {
            'net_ip': '$net_ip',
        },
            "gpu": {"$avg": "$gpu"},
            "temp": {"$avg": "$temp"},
            "percent": {"$avg": "$percent"},
            'net_ip': {"$first": "$net_ip"},
            'timestamp': {'$push': '$timestamp'}
        }},
    ]
    )

    with open(config_path, 'r') as f:
        conf = f.readlines()
    server_confi = []
    server_confi_dic = {}
    for dics in conf:
        dicc = eval(dics)
        server_confi.append(dicc['host'])
        server_confi_dic[dicc['host']] = dicc['name']

    aggre_obj = list(data_query)
    def total_hours(item):
        item['total_hours'] = len(item['timestamp']) * 0.5
        return item
    result = list(map(total_hours, aggre_obj))
    ip_arr = []
    for item in result:
        item = float2int(item)
        item['name'] = server_confi_dic[item['net_ip']]
        item.pop('_id')
        item['timestamp'] = max(item['timestamp'])
        ip_arr.append(item['net_ip'])

    list_dif = list(set(server_confi).difference(set(ip_arr)))

    for net_ip in list_dif:
        dic = dict(gpu=0, temp=0, percent=0, net_ip=net_ip, total_hours=0, name=server_confi_dic[net_ip])
        result.append(dic)
    # 正序
    students = Student.objects().all()
    students_all = list(map(lambda x: m2d_exclude(x), students))

    result_dic = {}
    for item in result:
        result_dic[item['net_ip']] = item

    for student in students_all:
        student['total_hours'] = 0
        for server_item in student['server']:
            if server_item['host'] in result_dic:
                student['total_hours'] += result_dic[server_item['host']]['total_hours']

    return result, students_all


if __name__ == '__main__':
    query_server("192.168.88.60")
    # query_all_user()
    # update_user('tf', name='ls')
    # query_server(ip="192.168.88.191")
    # result = section_hours_qurty(total_average_data)
    # result = section_total_hours_script_qurty(total_script_average_data)

    # result = section_hours_server(total_server_average_data)
    # with open('test.json', 'w') as f:
    #     json.dump(result, f, ensure_ascii=False, indent=4)
    # print(result)

    # query_week_server_hours()

    # now_free_server()

    # query_each_server_hours()

