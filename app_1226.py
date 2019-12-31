#!flask/bin/python
import json
import time,datetime
import os
import redis
import mongoengine
import socket
import pymysql
import paramiko
import copy
import uuid
import base64
import copy

from flask import Flask, render_template, jsonify, make_response,current_app
from flask import request
from model.Model_cp import *
from model.db import db_eng
from flask_cors import *
from utils_cc import *
from ceshi import *
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR ='/media/DiskData/TrainServer'
root = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.debug = False
app.config['SECRET_KEY'] = 'wiwide_lma'

# mongoengine.connect(db='monitor_copy', host='127.0.0.1:27017')
app.config['MONGODB_SETTINGS'] = {
    'db': 'monitor_copy',
    'host': '127.0.0.1',
    'port': 27017
}
with app.app_context():
    db_eng.init_app(app)

# conn = MongoClient('127.0.0.1', 27017)
# db = conn.monitor
# db = conn.monitor_copy
# moni_data = db.moni_data
# moni_script = db.moni_script

# schema = graphene.Schema(query=Query, mutation=Mutation)
# app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
config_path = root + '/config/config.txt'
monit_path = root + '/monitor_server.py'
del_path = root + '/monitor_del.py'
IMG_PATH = root + '/static/upload/'

UPLOAD_FOLDER = 'upload/'
DATA_FOLDER = 'data/'
DOWN_LOAD = DATA_FOLDER + 'logdir/'
HEADPIC_FOLDER = DATA_FOLDER + 'headpic/'

app.config['UPLOAD_FOLDER'] = 'static/uploads/'  # 保存文件位置

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/ceshi',methods=['POST'])
def ceshi():
    a = ces(DataD,ScriptS)
    print(a)
    return jsonify(err_ms=a)
# Data实例化
def tem_data(res):
    dics = {}
    dics['gpu_info'] = res.gpu_info
    dics['diskUsage'] = res.diskUsage
    # dics['gpu_version'] = res.gpu_version
    dics['cpuUsagePercent'] = res.cpuUsagePercent
    # dics['gpuUsagePercent'] = res.gpuUsagePercent
    dics['net_num'] = res.net_num
    dics['cpu_model'] = res.cpu_model
    dics['TotalMemory'] = res.TotalMemory
    dics['cpu_num'] = res.cpu_num
    # dics['pid_mess'] = res.pid_mess
    # dics['gpu_num'] = res.gpu_num
    # dics['net_ip'] = res.net_ip
    dics['timestamp'] = res.timestamp
    dics['UsageMemory'] = res.UsageMemory
    # dics['gpu_temperat'] = res.gpu_temperat
    dics['diskTotal'] = res.diskTotal
    return dics

# Scipt实例化
def tem_script(res):
    dics = {}
    dics['user'] = res.user
    dics['gpu_pid'] = res.gpu_pid
    dics['start_time'] = res.start_time
    dics['gpu_mem'] = res.gpu_mem
    dics['config'] = res.config
    dics['duration'] = res.duration
    dics['gpu_use'] = res.gpu_use
    dics['net_ip'] = res.net_ip
    dics['timestamp'] = res.timestamp
    return dics

# Student实例化
def tem_sudent(res):
    dics = {}
    dics['name'] = res.name
    dics['gender'] = res.gender
    dics['server'] = res.server
    dics['img_addr'] = res.img_addr
    dics['github'] = res.github
    dics['phone'] = res.phone
    dics['grade'] = res.grade
    dics['stuid'] = res.stuid
    dics['cardid'] = res.cardid
    return dics

# 平台登录
@app.route('/login',methods=['POST'])
def login():
    data = request.json
    if data:
        try:
            name = data['name']
            password = data['password']
            person = Person.objects(name=name,password=password)
            if len(person):
                dics = {}
                dics['name'] = person[0].name
                dics['password'] = person[0].password
                return jsonify(error_code=0, login='success', err_msg=dics)
            else:
                return jsonify(error_code=1, login='fail')
        except Exception as e:
            print(e)
            return jsonify(error_code=1, login='fail', err_msg=e)
    else:
        return jsonify(error_code=1,err_msg='json error')

# 平台注册信息
@app.route('/register',methods=['POST'])
def register():
    data = request.json
    if data:
        try:
            name = data['name']
            pwd = data['password']
            auth = data['auth']
            query_obj = Person.objects(name=name)
            if query_obj:
                return jsonify(error_code=1,status=400,err_msg='username is exist')
            else:
                post_obj = Person(name=name,password=pwd,auth=auth)
                post_obj.save()
                return jsonify(error_code=0,status=200,err_msg=200)
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 增加服务器信息
@app.route('/add_server',methods=['POST'])
def add_server():
    data = request.json
    print(data)
    if data:
        # server_dic = {}
        # server_dic['name'] = data['name']
        # server_dic['host'] = data['host']
        # server_dic['user'] = data['user']
        # server_dic['pwd'] = data['pwd']
        if "user" not in data:
            data['user'] = "user"
        if "pwd" not in data:
            data['pwd'] = "priv123"
        if "interval" not in data:
            data['interval'] = 1800
        timestamp = time.time()
        with open(config_path, 'r') as conf:
            txt_file = conf.readlines()
        try:

            ip_list = []
            name_list = []
            for dics in txt_file:
                dicc = eval(dics)
                ip_list.append(dicc['host'])
                name_list.append(dicc['name'])
            if data['host'] in ip_list or data['name'] in name_list:
                return jsonify(error_code=1, status=400,err_msg='ip or name is exist')
            else:
                resu = add_data(data['host'],data['user'],data['pwd'],data['interval'],moni_data, moni_script)
                if resu ==0:

                    return jsonify(error_code=1, status=400, err_msg='auth fail')
                else:
                    with open(config_path, 'a+') as conf:
                        conf.write(str(data) + '\n')
                    query_obj = Record(user=data['host'], opera="add_server", record=data, timestamp=int(timestamp))
                    query_obj.save()
                    return jsonify(error_code=0, status=200, err_msg=resu)
                    # 从data查询数据
                    # query_oo = Data.objects(net_ip=data['host']).order_by('-timestamp').limit(1)
                    # if query_oo:
                    #     list_at = []
                    #     for res in query_oo:
                    #         data = tem_data(res)
                    #         list_at.append(data)

                    # else:
                    #     print(resu)
                    #     return jsonify(error_code=1,status=400,err_msg='no data')

                # else:
                #     return jsonify(error_code=1,status=400,err_msg='system error')
        except Exception as e:
            print('***********')
            print(e)
            traceback.print_exc()
            print('***********')
            return jsonify(error_code=1,status=400, err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 修改服务器信息
@app.route('/edi_server',methods=['POST'])
def edi_server():
    data = request.json
    if data:
        old_data = data['old_data']
        new_data = data['new_data']
        try:
            old_ip = old_data['host']
            timestamp = time.time()
            with open(config_path,'r') as conf:
                txt_conf = conf.readlines()
            ip_list = []
            name_list = []
            for i in txt_conf:
                dic_ = eval(i)
                if dic_['host'] == old_data['host']:
                    if 'user' not in new_data:
                        new_data['user'] = dic_['user']
                    if 'pwd' not in new_data:
                        new_data['pwd'] = dic_['pwd']
                    if 'time' not in new_data:
                        new_data['interval'] = dic_['interval']
                ip_list.append(dic_['host'])
                name_list.append(dic_['name'])
            # 名字和ip不能和别的重复
            if new_data['name']!=old_data['name'] and new_data['name'] in name_list:
                return jsonify(error_code=1,status=400,err_msg='name exist')
            if new_data['host'] != old_data['host'] and new_data['host'] in ip_list:
                return jsonify(error_code=1,status=400,err_msg='ip exist')
            if old_ip in ip_list:
                if old_ip != new_data['host']:
                    resu = add_data(new_data['host'],new_data['user'],new_data['pwd'],new_data['interval'], moni_data, moni_script)
                    if resu==0:
                        # 返回错误的操作
                        return jsonify(error_code=1, status=400, err_msg='auth fail')
                    else:
                        with open(config_path, 'w')as f:
                            for value in txt_conf:
                                dic_obj = eval(value)
                                if old_ip == dic_obj['host']:
                                    f.write(str(new_data) + '\n')
                                else:
                                    f.write(value)
                        Data.objects(net_ip=old_ip).update(set__net_ip=new_data['host'])
                        Script.objects(net_ip=old_ip).update(set__net_ip=new_data['host'])
                        Record.objects(user=old_ip).update(set__user=new_data['host'])
                        query_obj = Record(user=new_data['host'], opera="edi_server", record=data,
                                           timestamp=int(timestamp))
                        query_obj.save()
                        return jsonify(error_code=0, status=200, err_msg=resu)

                else:
                    resu = edi_data(new_data['host'],new_data['user'],new_data['pwd'],new_data['interval'],moni_data,moni_script)
                    if resu == 0:
                        return jsonify(error_code=1, status=400, err_msg='auth fail')
                    else:
                        with open(config_path, 'w')as f:
                            for value in txt_conf:
                                dic_obj = eval(value)
                                if old_ip == dic_obj['host']:
                                    f.write(str(new_data) + '\n')
                                else:
                                    f.write(value)
                        # TODO 可优化 将写入文件放到后面减少返回错误的操作
                        query_obj = Record(user=new_data['host'], opera="edi_server", record=data, timestamp=int(timestamp))
                        query_obj.save()

                        return jsonify(error_code=0, status=200, err_msg=resu)
                # query_oo = Data.objects(net_ip=new_data['host']).order_by('-timestamp').limit(1)
                # list_at = []
                # if query_oo:
                #     for res in query_oo:
                #         data = tem_data(res)
                #         list_at.append(data)


            else:
                return jsonify(error_code=1,status=400,err_msg='old ip not exist')

        except Exception as e:
            print(e)
            with open(config_path, 'w') as conf:
                for value in txt_conf:
                    conf.write(value)
            return jsonify(error_code=1,status=400,err_msg=e)

    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 删除服务器
@app.route('/server_del',methods=['POST'])
def server_del():
    data = request.json
    if data:

        ip = data['host']
        timestamp = time.time()
        with open(config_path, 'r') as conf:
            txt_conf = conf.readlines()
        try:
            list_arr = []
            for i in txt_conf:
                confs = eval(i)
                list_arr.append(confs['host'])
            if ip in list_arr:
                with open(config_path,'w') as conf:
                    for value in txt_conf:
                        con_obj = eval(value)
                        if ip == con_obj['host']:
                            continue
                        conf.write(value)
                rec_obj = Record(user=ip, opera='del_server', record=data, timestamp=int(timestamp))
                rec_obj.save()
                # query_obj = Student.objects(server=ip)
                # if query_obj:
                #     query_obj.delete()
                # 暂时不删除
                # quer_obj = Data.objects(net_ip=ip)
                # if quer_obj:
                #     quer_obj.delete()
                # que_obj = Script.objects(net_ip=ip)
                # if que_obj:
                #     que_obj.delete()

                return jsonify(error_code=0,status=200,err_msg=200)
            else:
                return jsonify(error_code=1,status=400,err_msg='ip not exist')
        except Exception as e:
            print(e)
            ip_list = []
            old_dic  = ''
            for dics in txt_file:
                dicc = eval(dics)
                if data['host'] == dicc['host']:
                    old_dic = dics
                ip_list.append(dicc['host'])
            if old_dic:
                with open(config_path, 'a+') as conf:
                    conf.write(str(old_dic) + '\n')
            return jsonify(error_code=1,status=400,err_msg=e)

    else:
        return jsonify(error_code=1,err_msg='json error')

# 通过ip查找对应name
def ip_find(conf_obj,ip):
    for i in conf_obj:
        dic_ob = eval(i)
        if dic_ob['host']==ip:
            name = dic_ob['name']
            user = dic_ob['user']
            pwd  = dic_ob['pwd']
            time_interval = dic_ob['interval']
            return name,user,pwd,time_interval

def select_con_cc(s_time,Yestarday,ip,list_attr):
    data_query = Data._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": s_time, "$gte": Yestarday}, "net_ip": ip}},
        {"$sort": {"timestamp": -1}},
        {"$group": {"_id": "$net_ip",
                    "timestamp": {"$first": "$timestamp"},
                    "net_num": {"$first": "$net_num"},
                    "gpu_info": {"$first": "$gpu_info"},
                    "cpuUsagePercent": {"$first": "$cpuUsagePercent"},
                    "diskUsage": {"$first": "$diskUsage"},
                    "TotalMemory": {"$first": "$TotalMemory"},
                    "cpu_model": {"$first": "$cpu_model"},
                    "UsageMemory": {"$first": "$UsageMemory"},
                    "diskTotal": {"$first": "$diskTotal"},
                    "cpu_num": {"$first": "$cpu_num"},
                    }},
    ]
    )
    # gpu_use_list = Script.objects(timestamp__lte=s_time,timestamp__gte=Yestarday,net_ip=ip).distinct("gpu_use")
    # ccc = Script._get_collection().aggregate([
    #     {"$match": {"timestamp": {"$lte": s_time, "$gte": Yestarday}, "net_ip": ip}},
    #     {"$group":{"_id":"$gpu_use"}},
    #     {"$group": {"_id": "$gpu_use",
    #                 }},
    # ]
    # )
    aggre_obj = list(data_query)

    if aggre_obj:
        content_dic = aggre_obj[0]
        content_dic['net_ip'] = content_dic.pop('_id')
        list_adr = content_dic['gpu_info']
        if len(list_adr):
            for i in list_adr:
                gpu_use = i['fan']
                script_query = Script._get_collection().aggregate([
                    {"$match": {"timestamp": {"$lte": s_time, "$gte": Yestarday}, "net_ip": ip, "gpu_use": gpu_use}},
                    # {"$sort": {"timestamp": -1}},
                    {"$group": {"_id": "$gpu_use",
                                "gpu_mem": {"$avg": "$gpu_mem"}
                                }},
                ]
                )
                script_query = list(script_query)
                for j in i['script']:
                    if j['gpu_use'] == gpu_use:
                        j['gpu_mem'] = int(script_query[0]['gpu_mem'])

            list_attr.append(content_dic)
        else:
            list_attr.append(content_dic)
    # else:
    #     dicc = {}
    #     list_attr.append(dicc)
    return list_attr

def select_con(s_time,Yestarday,ip,list_attr):
    data_query = Data._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": s_time, "$gte": Yestarday}, "net_ip": ip}},
        {"$sort": {"timestamp": -1}},
        {'$unwind': '$gpu_info'},
        {"$group": {"_id": "$gpu_info.fan",
                    "gpu":{"$avg":"$gpu_info.usedMemry"},
                    "temp":{"$avg":"$gpu_info.temp"},
                    "percent":{"$avg":"$gpu_info.percent"}
                    }},
    ]
    )
    aggre_obj = list(data_query)

    if aggre_obj:
        # print(aggre_obj)
        first_data = Data.objects(timestamp__lte=s_time,timestamp__gte=Yestarday,net_ip=ip).order_by("-timestamp").first()
        if first_data:
            dics = tem_data(first_data)
            gpu_list = dics['gpu_info']
            for i in gpu_list:
                for diss in aggre_obj:
                    if i['fan'] == diss['_id']:
                        i['usedMemry'] = int(diss['gpu'])
                        i['percent'] = round(diss['percent'],2)
                        i['temp'] = int(diss['temp'])
            list_attr.append(dics)
    else:
        data = Data.objects(net_ip=ip).order_by('-timestamp').first()
        dicc = tem_data(data)
        dicc['diskUsage'] = 0
        dicc['UsageMemory'] = 0
        dicc['timestamp'] = Yestarday
        gpu_info = dicc['gpu_info']
        for gpu_dic in gpu_info:
            gpu_dic['gpu_mem'] = 0
            gpu_dic['usedMemry'] = 0
            gpu_dic['percent'] = 0
            gpu_dic['temp'] = 0
            gpu_dic['script'] = []
        list_attr.append(dicc)
    return list_attr

# 查询一周数据
@app.route('/week_data',methods=['POST'])
def week_data():
    data = request.json
    if data:
        start_time = int(data['start_time'])
        end_time = int(data['end_time'])
        ip_list = data['ip_list']
        # end = datetime.datetime.fromtimestamp(end_time)
        # time_diffe = (end - start).days
        with open(config_path, 'r') as conf:
            txt_file = conf.readlines()
        list_all = []
        for ip in ip_list:
            list_attr = []
            s_time = end_time

            for i in range(7):
                if i ==0:
                    timeArray = time.localtime(s_time)
                    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    # print(type(otherStyleTime))
                    # 获取当天0点时间+1天
                    startTime2 = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
                    zeroToday = startTime2 - datetime.timedelta(hours=startTime2.hour, minutes=startTime2.minute,
                                                            seconds=startTime2.second,
                                                            microseconds=startTime2.microsecond)
                    destarr = zeroToday.strftime("%Y-%m-%d %H:%M:%S")
                    timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                    Yestarday = int(time.mktime(timeArray))
                    list_attr = select_con(s_time,Yestarday,ip,list_attr)

                    s_time = int(time.mktime(timeArray))

                else:
                    timeArray = time.localtime(s_time)
                    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    # print(type(otherStyleTime))
                    # 获取当天0点时间+1天
                    startTime2 = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
                    zeroToday = startTime2 - datetime.timedelta(hours=startTime2.hour, minutes=startTime2.minute,
                                                                seconds=startTime2.second,
                                                                microseconds=startTime2.microsecond)
                    destarr = (zeroToday + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
                    timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                    Yestarday = int(time.mktime(timeArray))
                    list_attr = select_con(s_time,Yestarday,ip,list_attr)

                    s_time = int(time.mktime(timeArray))
            name,user,pwd,time_interval = ip_find(txt_file,ip)
            dic_one = {}
            dic_one['name'] = name
            dic_one['user'] = user
            dic_one['pwd'] = pwd
            dic_one['interval'] = time_interval
            dic_one['host'] = ip
            dic_one['data_info'] = list_attr
            list_all.append(dic_one)
        return jsonify(error_code=0, status=200, err_msg=list_all)
    else:
        return jsonify(error_code=1, status=400, err_msg='json error')

# 查询一周数据
@app.route('/week_data_cc',methods=['POST'])
def week_data_cc():
    data = request.json
    if data:
        start_time = int(data['start_time'])
        end_time = int(data['end_time'])
        ip_list = data['ip_list']
        # end = datetime.datetime.fromtimestamp(end_time)
        # time_diffe = (end - start).days
        with open(config_path, 'r') as conf:
            txt_file = conf.readlines()
        list_all = []
        for ip in ip_list:
            list_attr = []
            s_time = end_time

            for i in range(7):
                if i ==0:
                    timeArray = time.localtime(s_time)
                    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    # print(type(otherStyleTime))
                    # 获取当天0点时间+1天
                    startTime2 = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
                    zeroToday = startTime2 - datetime.timedelta(hours=startTime2.hour, minutes=startTime2.minute,
                                                            seconds=startTime2.second,
                                                            microseconds=startTime2.microsecond)
                    destarr = zeroToday.strftime("%Y-%m-%d %H:%M:%S")
                    timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                    Yestarday = int(time.mktime(timeArray))
                    list_attr = select_con(s_time,Yestarday,ip,list_attr)

                    s_time = int(time.mktime(timeArray))

                else:
                    timeArray = time.localtime(s_time)
                    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    # print(type(otherStyleTime))
                    # 获取当天0点时间+1天
                    startTime2 = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
                    zeroToday = startTime2 - datetime.timedelta(hours=startTime2.hour, minutes=startTime2.minute,
                                                                seconds=startTime2.second,
                                                                microseconds=startTime2.microsecond)
                    destarr = (zeroToday + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
                    timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                    Yestarday = int(time.mktime(timeArray))
                    list_attr = select_con(s_time,Yestarday,ip,list_attr)

                    s_time = int(time.mktime(timeArray))
                    
            name,user,pwd,time_interval = ip_find(txt_file,ip)
            dic_one = {}
            dic_one['name'] = name
            dic_one['user'] = user
            dic_one['pwd'] = pwd
            dic_one['interval'] = time_interval
            dic_one['host'] = ip
            dic_one['data_info'] = list_attr
            list_all.append(dic_one)
        return jsonify(error_code=0, status=200, err_msg=list_all)
    else:
        return jsonify(error_code=1, status=400, err_msg='json error')

# 查询所有服务器信息
@app.route('/all_server',methods=['POST'])
def all_server():
    try:
        with open(config_path, 'r') as conf:
            conf_obj = conf.readlines()
        list_arr = []
        for i in conf_obj:
            dic_ = eval(i)
            ip = dic_['host']
            name = dic_['name']
            user = dic_['user']
            pwd = dic_['pwd']
            time_interval = dic_['interval']
            query_res = Data.objects(net_ip=ip).order_by('-timestamp').limit(1)
            to_dic = {}
            if query_res:
                data_list = []
                for obj in query_res:
                    dics = tem_data(obj)
                    data_list.append(dics)

                to_dic['name'] = name
                to_dic['user'] = user
                to_dic['pwd'] = pwd
                to_dic['interval'] = time_interval
                to_dic['host'] = ip
                to_dic['data_info'] = data_list
                list_arr.append(to_dic)
            else:
                to_dic['name'] = name
                to_dic['user'] = user
                to_dic['pwd'] = pwd
                to_dic['interval'] = time_interval
                to_dic['host'] = ip
                to_dic['data_info'] = []
                list_arr.append(to_dic)

        return jsonify(error_code=0, status=200, err_msg=list_arr)

    except Exception as e:
        print(e)
        return jsonify(error_code=1,status=400,err_msg=e)


# TODO 通过server和server name查学生信息
@app.route('/server_stu',methods=['POST'])
def server_to_stu():
    data = request.json
    if data:
        ip_list = data['ip_list']
        total_list = []
        try:
            for ip_dic in ip_list:
                if 'host' not in ip_dic or 'name' not in ip_dic:
                    return jsonify(error_code=1, status=400, err_msg='host name not exist')
            for ip_dic in ip_list:
                dics = {}
                ip = ip_dic['host']
                name = ip_dic['name']
                stu_obj = Student._get_collection().find({"server":{"$elemMatch":{"host":ip,"name":name}}})
                stu_list = list(stu_obj)
                if stu_list:
                    for stu_dic in stu_list:
                        stu_dic.pop('_id')
                    dics['ip'] = ip
                    dics['data_info'] = stu_list
                    total_list.append(dics)
                else:
                    dics['ip'] = ip
                    dics['data_info'] = []
                    total_list.append(dics)
            return jsonify(error_code=0, status=200, err_msg=total_list)
        except Exception as e:
            print(e)
            return jsonify(error_code=1, status=400, err_msg=e)
    else:
        return jsonify(error_code=1, status=400, err_msg='json error')

# 根据时间段筛选数据
@app.route('/period_time',methods=['POST'])
def monitor():
    data = request.json
    if data:
        start_time = int(data['start_time'])
        end_time = int(data['end_time'])
        ip_list = data['ip_list']
        count = data['count']
        if not count:
            count = 1
        if count <= 0:
            count = 1
        time_diffe = end_time-start_time
        time_add = int(time_diffe / count)

        with open(config_path, 'r') as conf:
            conf_obj = conf.readlines()
        try:
            if len(ip_list) >= 1:
                all_list = []
                for ip in ip_list:
                    s_time = start_time
                    to_dic = {}
                    list_arr = []
                    for i in range(count):
                        start = datetime.datetime.fromtimestamp(s_time)
                        destarr = (start + datetime.timedelta(seconds=+time_add)).strftime("%Y-%m-%d %H:%M:%S")
                        timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                        Yestarday = int(time.mktime(timeArray))
                        list_arr = select_con(Yestarday,s_time,ip,list_arr)

                        s_time = int(time.mktime(timeArray))

                    # print(list_arr)
                    name, user, pwd, time_interval = ip_find(conf_obj, ip)
                    to_dic['name'] = name
                    to_dic['user'] = user
                    to_dic['pwd'] = pwd
                    to_dic['interval'] = time_interval
                    to_dic['host'] = ip
                    to_dic['data_info'] = list_arr
                    all_list.append(to_dic)
                return jsonify(error_code=0,status=200,err_msg=all_list)
            else:
                return jsonify(error_code=1,status=400,err_msg='no ip')
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)

    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 根据固定时间筛选,最近时间的数据
@app.route('/fixed_time',methods=['POST'])
def fixed_time():
    data = request.json
    if data:
        timestamp = int(data['timestamp'])
        ip_list = data['ip_list']
        with open(config_path, 'r') as conf:
            conf_obj = conf.readlines()
        try:
            if len(ip_list)>=1:
                list_attr = []
                for ip in ip_list:
                    on_a = Data.objects.filter(net_ip=ip,timestamp__lte=timestamp).order_by("-timestamp").limit(1)
                    next_a = Data.objects.filter(net_ip=ip,timestamp__gte=timestamp).order_by("timestamp").limit(1)
                    to_dic = {}
                    if on_a and next_a:
                        if timestamp-on_a[0].timestamp > timestamp-next_a[0].timestamp:
                            dics = tem_data(next_a[0])
                            name, user, pwd, time_interval = ip_find(conf_obj, ip)
                            to_dic['name'] = name
                            to_dic['user'] = user
                            to_dic['pwd'] = pwd
                            to_dic['interval'] = time_interval
                            to_dic['host'] = ip
                            to_dic['data_info'] = dics
                            list_attr.append(to_dic)

                        else:
                            dics = tem_data(on_a[0])
                            name, user, pwd, time_interval = ip_find(conf_obj, ip)
                            to_dic['name'] = name
                            to_dic['user'] = user
                            to_dic['pwd'] = pwd
                            to_dic['interval'] = time_interval
                            to_dic['host'] = ip
                            to_dic['data_info'] = dics
                            list_attr.append(to_dic)
                    else:
                        dict = {"ip":ip,"data_info":[]}
                        name, user, pwd, time_interval = ip_find(conf_obj, ip)
                        dict['name'] = name
                        dict['user'] = user
                        dict['pwd'] = pwd
                        dict['interval'] = time_interval
                        list_attr.append(dict)

                return jsonify(error_code=0,status=200,err_msg=list_attr)
            else:
                return jsonify(error_code=1,status=400,err_msg='no ip')
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_ms ='json error')

# 查询当前时间到24小时前的数据
@app.route('/one_day',methods=['POST'])
def one_day():
    data = request.json
    if data:
        timestamp = int(data['timestamp'])
        ip_list = data['ip_list']
        with open(config_path, 'r') as conf:
            conf_obj = conf.readlines()
        # timeArray = time.localtime(timestamp)
        # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        # dateArray = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
        # dateStr = (dateArray + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
        # timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        one_dat_time = int(timestamp-60*60*24)
        try:
            if len(ip_list)>=1:
                all_list = []
                for ip in ip_list:
                    to_dic = {}
                    list_arr = []
                    query_res = Data.objects(net_ip=ip,timestamp__gte=one_dat_time,timestamp__lte=timestamp)
                    if query_res:
                        for res in query_res:
                            dics = tem_data(res)
                            list_arr.append(dics)
                    # print(list_arr)
                    name, user, pwd, time_interval = ip_find(conf_obj, ip)
                    to_dic['name'] = name
                    to_dic['user'] = user
                    to_dic['pwd'] = pwd
                    to_dic['interval'] = time_interval
                    to_dic['host'] = ip
                    to_dic['data_info'] = list_arr
                    all_list.append(to_dic)
                return jsonify(error_code=0,status=200,err_msg=all_list)
            else:
                return jsonify(error_code=1,status=400,err_msg='no ip')

        except Exception as e:
            print(e)
            return jsonify(error_code=1, status=400,err_msg=e)

    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 给图片命名
def img_pat():
    uuid_str = uuid.uuid4().hex
    img_path = IMG_PATH + uuid_str + '.jpg'
    if os.path.exists(img_path):
        img_pat()
    else:
        return img_path

# 简单判断是否是base64
def is_base64_code(s):
    '''Check s is Base64.b64encode'''
    if not isinstance(s ,str):
        return False
    if ',' in s:
        s= s.split(',')[1]
    _base64_code = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I',
                    'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
                    'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a',
                    'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
                    'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
                    't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1',
                    '2', '3', '4','5', '6', '7', '8', '9', '+',
                    '/', '=']

    # Check base64 OR codeCheck % 4
    code_fail = [ i for i in s if i not in _base64_code]
    if code_fail or len(s) % 4 != 0:
        return False
    return s


# 学生添加
# TODO 图片存储
@app.route('/stu_add',methods=['POST'])
def student_add():
    data = request.json
    timestamp = time.time()

    if data:
        with open(config_path, 'r') as conf:
            txt_file = conf.readlines()
        ip_list = []
        for dics in txt_file:
            dicc = eval(dics)
            ip_list.append(dicc['host'])

        if 'name' not in data or 'grade' not in data or 'stuid' not in data:
            return jsonify(error_code=1, status=400, err_msg='name grade stuid is null')
        if not ['name'] or not ['grade'] or not ['grade']:
            return jsonify(error_code=1,status=400, err_msg='{} or {} or {} no value'.format(data['name'],data['grade'],data['stuid']))


        if 'server' not in data or not data['server']:
            data['server'] = []
        if 'github' not in data or not data['github']:
            data['github'] = ''
        if 'phone' not in data or not data['phone']:
            data['phone'] = 0
        if 'cardid' not in data or not data['cardid']:
            data['cardid'] = 0
        if 'img_addr' not in data:
            data['img_addr'] = ''
        if 'gender' not in data or not data['gender']:
            data['gender'] = 0
        if data['gender'] != 0 and data['gender'] !=1:
            return jsonify(error_code=1,status=400,err_msg='gender send 0 or 1')

        try:
            query_id = Student.objects(stuid=data['stuid'])
            if query_id:
                return jsonify(error_code=1,status=400,err_msg='stuid {} is exist'.format(data['stuid']))

            query_obj = Student.objects(name=data['name'],grade=data['grade'])
            if query_obj:
                return jsonify(error_code=1,status=400,err_msg='{} {} is exist'.format(data['name'],data['grade']))
            else:

                # 获取学生最新数据
                total_list = []
                if data['server']:

                    for ip_dic in data['server']:
                        # TODO暂未将数据分开
                        list_attr = []
                        ip = ip_dic['host']
                        user = ip_dic['user']
                        # script_obj = Script.objects(net_ip=ip,user=data['name'])
                        # if script_obj:
                        # 通过ip和name对gpu_use去重 并筛选出每个去重字段的最新数据
                        scrip_obj = Script._get_collection().aggregate([
                            {"$match": {"net_ip": ip, "user": user}},
                            {"$sort": {"timestamp": -1}},
                            {"$group": {"_id": {"gpu_use": "$gpu_use"}, "data": {"$first": "$$ROOT"}}},
                            {"$project": {"data": 1}},
                        ])
                        script_list = list(scrip_obj)
                        if script_list:
                            for scr in script_list:
                                scri_dic = scr['data']
                                scri_dic.pop('_id')
                                list_attr.append(scri_dic)

                        total_list.append(list_attr)

                # img_addr = data['img_addr']
                if data['img_addr']:
                    img_base64 = is_base64_code(data['img_addr'])
                    if img_base64:
                        imagedata = base64.b64decode(img_base64)
                        img_path = img_pat()
                        with open(img_path,'wb') as f:
                            f.write(imagedata)
                        data['img_addr'] = '/static/upload/'+img_path.split('/')[-1]
                    else:
                        return jsonify(error_code=1,status=400,err_msg='base64 coding error')

                data['data_info'] = total_list
                # dic_all['name'] = data['name']
                # dic_all['gender'] = data['gender']
                data['img_addr'] = data['img_addr']
                # dic_all['github'] = data['github']
                # dic_all['grade'] = data['grade']
                # dic_all['phone'] = data['phone']
                # dic_all['server'] = data['server']
                # dic_all['stuid'] = data['stuid']
                # dic_all['cardid'] = data['cardid']

                post_obj = Student(name=data['name'], gender=data['gender'], server=data['server'], img_addr=data['img_addr'],
                                   github=data['github'], grade=data['grade'], phone=data['phone'],stuid=data['stuid'],cardid=data['cardid'])
                post_obj.save()
                rec_obj = Record(user=data['name'], opera='add', record=data, timestamp=int(timestamp))
                rec_obj.save()
                return jsonify(error_code=0,status=200, err_msg=data)
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 学生删除
@app.route('/stu_del',methods=['POST'])
def student_del():
    data = request.json
    timestamp = time.time()
    if data:
        # 传user列表
        name_list = data['student']
        try:
            for name_dic in name_list:
                if 'name' and 'grade' not in name_dic:
                    return jsonify(error_code=1,status=400,err_msg='not keyword name grade')
            list_all = []
            for name_dic in name_list:
                name = name_dic['name']
                grade = name_dic['grade']
                query_obj = Student.objects(name=name,grade=grade)
                dicc = {}
                if query_obj:
                    img_path = query_obj[0].img_addr
                    img_re_path = root+img_path
                    # 删除图片
                    if os.path.exists(img_re_path) and not os.path.isdir(img_re_path):
                        os.remove(root+img_path)
                    # query_ob = Script.objects(user=name)
                    # if query_ob:
                    #     query_ob.delete()
                    query_obj.delete()
                    rec_obj = Record(user=name,opera='del',record=data,timestamp=int(timestamp))
                    rec_obj.save()
                    dicc['name'] = name
                    dicc['grade'] = grade
                    # 表示删除
                    dicc['status'] = 0
                    list_all.append(dicc)
                else:
                    dicc['name'] = name
                    dicc['grade'] = grade
                    # 表示未删除
                    dicc['status'] = 1
                    list_all.append(dicc)
            return jsonify(error_code=0,status=200,err_msg=list_all)
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=str(e))

    else:
        return jsonify(error_code=1,status=400,err_msg='json error')
# 学生编辑
# 改什么传什么，列表将原来未修改的值带上
@app.route('/stu_edi',methods=['POST'])
def student_edi():
    data = request.json
    timestamp = time.time()
    if data:
        old_data = data['old_data']
        new_data = data['new_data']
        name = old_data['name']
        grade = old_data['grade']
        stuid = old_data['stuid']
        with open(config_path, 'r') as conf:
            txt_file = conf.readlines()
        ip_list = []
        for dics in txt_file:
            dicc = eval(dics)
            ip_list.append(dicc['host'])
        try:
            query_obj = Student.objects(name=name, grade=grade).first()
            if query_obj:
                #

                # 查询修改的姓名 年级是否存在
                if not (name == new_data['name'] and grade == new_data['grade'] and stuid==new_data['stuid']):
                    id_obj = Student.objects(stuid=new_data['stuid'])
                    if id_obj:
                        return jsonify(error_code=1,status=400,err_msg='stuid {} is exist'.format(new_data['stuid']))
                    new_obj = Student.objects(name=new_data['name'], grade=new_data['grade'])
                    if new_obj:
                        return jsonify(error_code=1, status=400,
                                       err_msg='{} and {} is exist'.format(new_data['name'], new_data['grade']))
                # 查看server是否在里面
                if 'server' in new_data:
                    if new_data['server']:
                        for server in new_data['server']:
                            ip = server['host']
                            if 'user' and 'pwd' not in server:
                                server['user'] = 'user'
                                server['pwd'] = 'priv123'
                            if 'host' not in server:
                                return jsonify(error_code=1,status=400,err_msg='host not exist')
                            if ip not in ip_list:
                                return jsonify(error_code=1,status=400,err_msg='{} not exit'.format(ip))
                    else:
                        new_data['server'] = []

                if name != new_data['name']:
                    Script.objects(user=name).update(set__user=new_data['name'])

                for key, value in new_data.items():
                    if key == 'img_addr':
                        img_base64 = is_base64_code(value)
                        if img_base64:
                            imagedata = base64.b64decode(img_base64)
                            img_path = img_pat()
                            with open(img_path, 'wb') as f:
                                f.write(imagedata)
                            new_img_path = '/static/upload/' + img_path.split('/')[-1]
                            setattr(query_obj, key, new_img_path)
                        else:
                            print("****")
                            value = '/{}'.format(value.split('/', 3)[-1])
                            print(value)
                            setattr(query_obj,key,value)
                    else:
                        setattr(query_obj,key,value)
                query_obj.save()
                total_list = []
                if query_obj['server']:
                    for server in query_obj['server']:
                        ip = server['host']
                        user = server['user']
                        list_attr = []
                        scrip_obj = Script._get_collection().aggregate([
                            {"$match": {"net_ip": ip, "user": user}},
                            {"$sort": {"timestamp": -1}},
                            {"$group": {"_id": {"gpu_use": "$gpu_use"}, "data": {"$first": "$$ROOT"}}},
                            {"$project": {"data": 1}},
                        ])
                        script_list = list(scrip_obj)
                        if script_list:
                            for scr in script_list:
                                scri_dic = scr['data']
                                scri_dic.pop('_id')
                                list_attr.append(scri_dic)
                        total_list.append(list_attr)

                dic_all = tem_sudent(query_obj)
                dic_all['data_info'] = total_list
                # dic_all['name'] = query_obj['name']
                # dic_all['gender'] = query_obj['gender']
                # dic_all['img_addr'] = query_obj['img_addr']
                # dic_all['github'] = query_obj['github']
                # dic_all['grade'] = query_obj['grade']
                # dic_all['phone'] = query_obj['phone']
                # dic_all['server'] = query_obj['server']

                rec_obj = Record(user=name, opera='upd', record=data, timestamp=int(timestamp))
                rec_obj.save()

                return jsonify(error_code=0,status=200,err_msg=dic_all)
            else:
                return jsonify(error_code=1,status=400,err_msg='old name or grade not exist')

        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 所有学生查询
@app.route('/stu_sel',methods=['POST'])
def student_sel():
    timestamp = int(time.time())
    # timeArray = time.localtime(timestamp)
    one_dat_time = timestamp-60*60*24
    # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # dateArray = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    # dateStr = (dateArray + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    # timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
    query_set = Student.objects.all()
    if query_set:
        try:
            list_arr = []
            for stu in query_set:

                query_obj = tem_sudent(stu)
                name = stu.name
                server = stu.server
                # 从小到大
                total_list = []
                for ip_dic in server:
                    data_list = []
                    ip = ip_dic['host']
                    user = ip_dic['user']
                    # query_scipt = Script.objects(user=name,net_ip=ip).filter(timestamp__gte=one_dat_time,timestamp__lte=timestamp).order_by("-timestamp").limit(1)
                    scrip_obj = Script._get_collection().aggregate([
                        {"$match": {"net_ip": ip, "user": user,"timestamp": {"$lte": timestamp, "$gte": one_dat_time}}},
                        {"$sort": {"timestamp": -1}},
                        {"$group": {"_id": {"gpu_use": "$gpu_use"}, "data": {"$first": "$$ROOT"}}},
                        {"$project": {"data": 1}},
                    ])
                    script_list = list(scrip_obj)
                    if script_list:
                        for scr in script_list:
                            scri_dic = scr['data']
                            scri_dic.pop('_id')
                            data_list.append(scri_dic)
                    total_list.append(data_list)
                query_obj['data_info'] = total_list
                list_arr.append(query_obj)

            return jsonify(error_code=0,status=200,err_msg=list_arr)
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='no data')


def stu_value_0(ip,user,data_list,s_time,Yestarday):
    scrip_obj = Script._get_collection().aggregate([
        {"$match": {"net_ip": ip, "user": user}},
        {"$group": {"_id": "$gpu_use"}},
        {"$group": {"_id": 1, "count": {"$sum": 1}}},
    ])
    scrip_obj = list(scrip_obj)
    if scrip_obj:
        num = scrip_obj[0]['count']
        for nums in range(num):
            dicx = {'net_ip': ip, 'gpu_mem': 0, 'user': user, 'timestamp': Yestarday, 'config': '',
                    'start_time': '', 'duration': '', 'gpu_pid': 0}
            dicx['gpu_use'] = nums
            data_list.append(dicx)
    else:
        dicx = {'net_ip': ip, 'gpu_mem': 0, 'user': user, 'timestamp': Yestarday, 'config': '',
                'start_time': '', 'duration': '', 'gpu_pid': 0, 'gpu_use': 0}
        data_list.append(dicx)

    return data_list

# 所有学生查询
@app.route('/stu_all', methods=['POST'])
def student_all():
    timestamp = int(time.time())
    # timeArray = time.localtime(timestamp)
    one_dat_time = timestamp - 60 * 60 * 12
    # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # dateArray = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    # dateStr = (dateArray + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    # timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
    time_add = 60*60
    count = 12
    query_set = Student.objects.all()
    if query_set:
        try:
            list_arr = []
            for stu in query_set:

                query_obj = tem_sudent(stu)
                server = stu.server
                # 从小到大
                total_list = []
                for ip_dic in server:
                    data_list = []
                    ip = ip_dic['host']
                    user = ip_dic['user']
                    s_time = timestamp
                    for i in range(count):
                        Yestarday = s_time - time_add
                        aggre_obj = Script._get_collection().aggregate([
                            {"$match": {"net_ip": ip, "user": user,
                                        "timestamp": {"$lte": s_time, "$gte": Yestarday}}},
                            {"$sort": {"timestamp": -1}},
                            {"$group": {"_id": {"gpu_use": "$gpu_use"}, "data": {"$first": "$$ROOT"}}},
                            {"$project": {"data": 1}},
                        ])
                        aggre_obj = list(aggre_obj)
                        if aggre_obj:
                            for agg_con in aggre_obj:
                                scri_dic = agg_con['data']
                                scri_dic.pop('_id')
                                data_list.append(scri_dic)
                        else:
                            data_list = stu_value_0(ip,user,data_list,'',Yestarday)
                        s_time = s_time - time_add

                    # query_scipt = Script.objects(user=user, net_ip=ip).filter(timestamp__gte=one_dat_time,
                    #                                                           timestamp__lte=timestamp)
                    #
                    # if query_scipt:
                    #     # print(query_scipt.count())
                    #     for scr in query_scipt:
                    #         scr_dic = tem_script(scr)
                    #         data_list.append(scr_dic)
                    # else:
                    #     dicc = {}
                    #     data_list.append(dicc)
                    total_list.append(data_list)
                query_obj['data_info'] = total_list
                list_arr.append(query_obj)
            return jsonify(error_code=0, status=200, err_msg=list_arr)
        except Exception as e:
            print(e)
            return jsonify(error_code=1, status=400, err_msg=e)
    else:
        return jsonify(error_code=1, status=400, err_msg='no data')

# 所有学生查询
@app.route('/stu_all_ss', methods=['POST'])
def stu_all_ss():
    timestamp = int(time.time())
    # timeArray = time.localtime(timestamp)
    one_dat_time = timestamp - 60 * 60 * 8
    # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # dateArray = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    # dateStr = (dateArray + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    # timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
    time_add = 60*60
    count = 8
    query_set = Student.objects.all()
    if query_set:
        try:
            list_arr = []
            for stu in query_set:

                query_obj = tem_sudent(stu)
                server = stu.server
                # 从小到大
                total_list = []
                for ip_dic in server:

                    ip = ip_dic['host']
                    user = ip_dic['user']
                    s_time = timestamp
                    data_list = []
                    for i in range(count):

                        Yestarday = s_time - time_add
                        aggre_obj = Script._get_collection().aggregate([
                            {"$match": {"net_ip": ip, "user": user,
                                        "timestamp": {"$lte": s_time, "$gt": Yestarday}}},
                            {"$sort": {"timestamp": -1}},
                            {"$group": {"_id": {"gpu_use": "$gpu_use"}, "timestamp": {"$first": "$timestamp"},
                                        "net_ip": {"$first": "$net_ip"},
                                        "gpu_pid": {"$first": "$gpu_pid"},
                                        "start_time": {"$first": "$start_time"},
                                        "config": {"$first": "$config"},
                                        "duration": {"$first": "$duration"},
                                        "gpu_use": {"$first": "$gpu_use"},
                                        "gpu_mem": {"$avg": "$gpu_mem"},
                                        "user": {"$first": "$user"},
                            }},
                            # {"$project": {"data": 1}},
                        ])
                        aggre_obj = list(aggre_obj)
                        if aggre_obj:
                            for agg_con in aggre_obj:
                                agg_con.pop("_id")
                                data_list.append(agg_con)
                        else:
                            # 查询有几卡
                            aggre_obj = Script._get_collection().aggregate([
                                {"$match": {"net_ip": ip,"user":user}},
                                {"$group": {"_id": "$gpu_use"}},
                                {"$group": {"_id": 1, "count": {"$sum": 1}}}
                            ])
                            aggre_obj = list(aggre_obj)
                            if aggre_obj:
                                for i in range(aggre_obj[0]['count']):
                                    dicx = {'net_ip': ip, 'gpu_mem': 0, 'user': user, 'timestamp': Yestarday, 'config': '',
                                            'start_time': '', 'duration': '', 'gpu_pid': 0}
                                    dicx['gpu_use'] = i
                                    data_list.append(dicx)
                            else:
                                dicx = {'net_ip': ip, 'gpu_mem': 0, 'user': user, 'timestamp': Yestarday, 'config': '',
                                        'start_time': '', 'duration': '', 'gpu_pid': 0,'gpu_use':0}
                                data_list.append(dicx)
                        s_time = s_time - time_add

                    # query_scipt = Script.objects(user=user, net_ip=ip).filter(timestamp__gte=one_dat_time,
                    #                                                           timestamp__lte=timestamp)
                    #
                    # if query_scipt:
                    #     # print(query_scipt.count())
                    #     for scr in query_scipt:
                    #         scr_dic = tem_script(scr)
                    #         data_list.append(scr_dic)
                    # else:
                    #     dicc = {}
                    #     data_list.append(dicc)
                    total_list.append(data_list)
                query_obj['data_info'] = total_list
                list_arr.append(query_obj)
            return jsonify(error_code=0, status=200, err_msg=list_arr)
        except Exception as e:
            print(e)
            return jsonify(error_code=1, status=400, err_msg=e)
    else:
        return jsonify(error_code=1, status=400, err_msg='no data')

# 所有学生查询
@app.route('/stu_all_error_test',methods=['POST'])
def stu_all_error_test():
    timestamp = int(time.time())
    # timeArray = time.localtime(timestamp)
    one_dat_time = timestamp-60*60*24
    # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    # dateArray = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    # dateStr = (dateArray + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    # timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
    query_set = Student.objects.all()
    if query_set:
        try:
            list_arr = []
            for stu in query_set:

                query_obj = tem_sudent(stu)
                name = stu.name
                server = stu.server
                # 从小到大
                total_list = []
                for ip_dic in server:
                    data_list = []
                    ip = ip_dic['host']
                    user = ip_dic['user']
                    query_scipt = Script.objects(user=user,net_ip=ip).filter(timestamp__gte=one_dat_time,timestamp__lte=timestamp)
                    if query_scipt:
                        for scr in query_scipt:
                            scr_dic = tem_script(scr)
                            data_list.append(scr_dic)
                    # else:
                    #     dicc = {}
                    #     data_list.append(dicc)
                    total_list.append(data_list)
                query_obj['data_info'] = total_list
             
                list_arr.append(query_obj)
            return jsonify(error_code=0,status=200,err_msg=list_arr, asd=list_arr)
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='no data')


def select_scrip(s_time,Yestarday,list_attr,user,ip):
    aggre_obj = Script._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": s_time, "$gte": Yestarday}, "user": user,"net_ip":ip}},
        {"$sort": {"timestamp": -1}},
        {"$group": {"_id": "$user",
                    "timestamp": {"$first": "$timestamp"},
                    "net_ip": {"$first": "$net_ip"},
                    "gpu_pid": {"$first": "$gpu_pid"},
                    "start_time": {"$first": "$start_time"},
                    "config": {"$first": "$config"},
                    "duration": {"$first": "$duration"},
                    "gpu_use": {"$first": "$gpu_use"},
                    "gpu_mem": {"$avg": "$gpu_mem"}
                    }},
    ]
    )

    aggre_obj = list(aggre_obj)
    if aggre_obj:
        for agg_con in aggre_obj:
            agg_con['user'] = agg_con.pop("_id")
            list_attr.append(agg_con)
    else:
        # aggre_obj = Script._get_collection().aggregate([
        #     {"$match": {"net_ip": ip, "user": user}},
        #     {"$group": {"_id": "$gpu_use"}},
        #     {"$group": {"_id": 1, "count": {"$sum": 1}}}
        # ])
        # aggre_obj = list(aggre_obj)
        # if aggre_obj:
        #     for i in range(aggre_obj[0]['count']):
        #         dicx = {'net_ip': ip, 'gpu_mem': 0, 'user': user, 'timestamp': Yestarday, 'config': '',
        #                 'start_time': '', 'duration': '', 'gpu_pid': 0}
        #         dicx['gpu_use'] = i
        #         list_attr.append(dicx)
        # else:
        #     dicx = {'net_ip': ip, 'gpu_mem': 0, 'user': user, 'timestamp': Yestarday, 'config': '',
        #             'start_time': '', 'duration': '', 'gpu_pid': 0, 'gpu_use': 0}
        #     list_attr.append(dicx)
        list_attr = stu_value_0(ip,user,list_attr,'',Yestarday)
    return list_attr

def select_scrip_cc(s_time,Yestarday,list_attr,user,ip):
    aggre_obj = Script._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": s_time, "$gte": Yestarday}, "user": user,"net_ip":ip}},
        {"$sort": {"timestamp": -1}},
        {"$group": {"_id": "$user",
                    "timestamp": {"$first": "$timestamp"},
                    "net_ip": {"$first": "$net_ip"},
                    "gpu_pid": {"$first": "$gpu_pid"},
                    "start_time": {"$first": "$start_time"},
                    "config": {"$first": "$config"},
                    "duration": {"$first": "$duration"},
                    "gpu_use": {"$first": "$gpu_use"},
                    "gpu_mem": {"$avg":"$gpu_mem"}
                    }},
    ]
    )

    aggre_obj = list(aggre_obj)
    if aggre_obj:
        for agg_con in aggre_obj:
            agg_con['user'] = agg_con.pop("_id")
            agg_con['gpu_mem'] = int(agg_con['gpu_mem'])
            list_attr.append(agg_con)
    else:
        data_obj = Data.objects(net_ip=ip).first()
        if data_obj:
            dics = tem_data(data_obj)
            gpu_info = dics['gpu_info']
            gpu_count = len(gpu_info)
            # print(s_time,Yestarday)
            for i in range(gpu_count):
                dicx = {'net_ip': ip, 'gpu_mem': 0, 'user': user, 'timestamp': Yestarday, 'config': '',
                        'start_time': '', 'duration': '', 'gpu_pid': 0,'gpu_use':i}
                list_attr.append(dicx)
        # print(list_attr)
    return list_attr

# 查询某个时间段的数据
@app.route('/stu_period_time',methods=['POST'])
def stu_period_time():
    data = request.json
    if data:
        try:
            start_time = int(data['start_time'])
            end_time = int(data['end_time'])
            name_list = data['student']
            count = data['count']
            if not count:
                count = 1
            if count <= 0:
                count = 1
            time_diffe = end_time - start_time
            time_add = int(time_diffe / count)
            total_list = []
            for name_dic in name_list:
                name = name_dic['name']
                grade = name_dic['grade']
                stu_obj = Student.objects(name=name, grade=grade).first()
                if stu_obj:
                    stu_dic = tem_sudent(stu_obj)
                    server_list = stu_dic['server']
                    list_all = []
                    for ip_dic in server_list:
                        ip = ip_dic['host']
                        user = ip_dic['user']
                        list_arr = []
                        s_time = start_time
                        for i in range(count):
                            Yestarday = int(s_time) + time_add
                            list_arr = select_scrip(Yestarday,s_time,list_arr,user,ip)
                            s_time = int(s_time)+time_add

                        list_all.append(list_arr)
                    stu_dic['data_info'] = list_all
                    total_list.append(stu_dic)
                else:
                    return jsonify(error_code=1,status=400,err_msg='{} {} not exist'.format(name,grade))
            return jsonify(error_code=0,status=200,err_msg = total_list)
        except Exception as e:
            print(e)
            return jsonify(error_code=1, status=400, err_msg=e)
    else:
        return jsonify(error_code=1, status=400, err_msg='json error')

# 查询7天的数据
# TODO 对时间进行拆分7天获取7条数据
@app.route('/stu_week_data_cc',methods=['POST'])
def stu_week_data_cc():
    data = request.json
    if data:
        start_time = data['start_time']
        end_time = data['end_time']
        name_list = data['student']

        list_total = []
        try:
            for name_dic in name_list:
                name = name_dic['name']
                grade = name_dic['grade']
                stu_obj = Student.objects(name=name, grade=grade).first()
                if stu_obj:
                    stu_dic = tem_sudent(stu_obj)
                    server_list =stu_dic['server']

                    list_all = []

                    for ip_dic in server_list:
                        s_time = end_time
                        list_attr = []
                        for i in range(7):
                            ip = ip_dic['host']
                            user = ip_dic['user']
                            if i == 0:
                                # 获取零点时间戳
                                Yestarday = int(s_time - s_time % 86400 + time.timezone)
                                list_attr = select_scrip_cc(Yestarday, s_time, list_attr, user,ip)
                                s_time = int(s_time - s_time % 86400 + time.timezone)
                            else:
                                Yestarday = int(s_time)-60*60*24
                                list_attr = select_scrip_cc(s_time, Yestarday, list_attr, user,ip)
                                s_time = int(s_time)-60*60*24
                        list_all.append(list_attr)

                    stu_dic['data_info'] = list_all
                    list_total.append(stu_dic)
                else:
                    return jsonify(error_code=1, status=400, err_msg='{} {} not exist'.format(name,grade))
            return jsonify(error_code=0, status=200, err_msg=list_total)
        except Exception as e:
            print(e)
            return jsonify(error_code=1, status=400, err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')


# 查询7天的数据
# TODO 对时间进行拆分7天获取7条数据
@app.route('/stu_week_data',methods=['POST'])
def stu_week_data():
    data = request.json
    if data:
        start_time = data['start_time']
        end_time = data['end_time']
        name_list = data['student']
        # end = datetime.datetime.fromtimestamp(end_time)
        # time_diffe = (end - start).days
        list_total = []
        try:
            for name_dic in name_list:
                name = name_dic['name']
                grade = name_dic['grade']
                stu_obj = Student.objects(name=name, grade=grade).first()
                if stu_obj:
                    stu_dic = tem_sudent(stu_obj)
                    server_list =stu_dic['server']

                    list_all = []

                    for ip_dic in server_list:
                        s_time = end_time
                        list_attr = []
                        for i in range(7):
                            ip = ip_dic['host']
                            user = ip_dic['user']
                            if i == 0:
                                # timeArray = time.localtime(s_time)
                                # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                # # print(type(otherStyleTime))
                                # # 获取当天0点时间+1天
                                # startTime2 = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
                                # zeroToday = startTime2 - datetime.timedelta(hours=startTime2.hour, minutes=startTime2.minute,
                                #                                             seconds=startTime2.second,
                                #                                             microseconds=startTime2.microsecond)
                                # destarr = zeroToday.strftime("%Y-%m-%d %H:%M:%S")
                                # timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                                # Yestarday = int(time.mktime(timeArray))
                                Yestarday = int(s_time - s_time % 86400 + time.timezone)
                                list_attr = select_scrip(Yestarday, s_time, list_attr, user,ip)
                                s_time = int(s_time - s_time % 86400 + time.timezone)
                                # s_time = int(time.mktime(timeArray))
                            else:
                                # timeArray = time.localtime(s_time)
                                # otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                                # # print(type(otherStyleTime))
                                # # 获取当天0点时间+1天
                                # startTime2 = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
                                # zeroToday = startTime2 - datetime.timedelta(hours=startTime2.hour, minutes=startTime2.minute,
                                #                                             seconds=startTime2.second,
                                #                                             microseconds=startTime2.microsecond)
                                # destarr = (zeroToday + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
                                # timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                                # Yestarday = int(time.mktime(timeArray))
                                Yestarday = int(s_time) - 60 * 60 * 24
                                list_attr = select_scrip(s_time, Yestarday, list_attr, user,ip)
                                s_time = int(s_time) - 60 * 60 * 24
                                # s_time = int(time.mktime(timeArray))
                        list_all.append(list_attr)

                    stu_dic['data_info'] = list_all
                    list_total.append(stu_dic)
                else:
                    return jsonify(error_code=1, status=400, err_msg='{} {} not exist'.format(name,grade))
            return jsonify(error_code=0, status=200, err_msg=list_total)
        except Exception as e:
            print(e)
            return jsonify(error_code=1, status=400, err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 学生根据最近时间进行查询
@app.route('/stu_fixed_time',methods=['POST'])
def stu_fixed_time():
    data = request.json
    if data:
        try:
            timestamp = data['timestamp']
            name_list = data['student']
            total_list = []
            for name_dic in name_list:
                name = name_dic['name']
                grade = name_dic['grade']
                stu_obj = Student.objects(name=name,grade=grade).first()
                if stu_obj:
                    stu_dic = tem_sudent(stu_obj)
                    server_list = stu_dic['server']
                    list_all = []

                    for ip_dic in server_list:
                        ip = ip_dic['host']
                        user = ip_dic['user']
                        list_attr = []
                        on_a = Script.objects(user=user,net_ip=ip,timestamp__lte=timestamp).order_by("-timestamp").limit(1)
                        # print(on_a[0].timestamp)
                        next_a = Script.objects(user=user,net_ip=ip,timestamp__gte=timestamp).order_by("timestamp").limit(1)
                        # print(next_a[0].timestamp)
                        # dics = {}
                        if on_a and next_a:
                            if timestamp - on_a[0].timestamp > timestamp - next_a[0].timestamp:
                                dics = tem_script(next_a[0])
                                list_attr.append(dics)
                            else:
                                dics = tem_script(on_a[0])
                                list_attr.append(dics)
                        elif on_a and not next_a:
                            dics = tem_script(on_a[0])
                            list_attr.append(dics)
                        elif not on_a and next_a:
                            dics = tem_script(next_a[0])
                            list_attr.append(dics)
                        else:
                            dicx = {'net_ip': ip, 'gpu_mem': 0, 'user': user, 'timestamp': Yestarday, 'config': '',
                                    'start_time': '', 'duration': '', 'gpu_pid': 0, 'gpu_use': 0}
                            list_attr.append(dicx)

                        list_all.append(list_attr)
                    stu_dic['data_info'] = list_all
                    total_list.append(stu_dic)
                else:
                    return jsonify(error_code=1, status=400, err_msg='{} {} not exist'.format(name,grade))
            return jsonify(error_code=0, status=200, err_msg=total_list)
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 根据当前时间查看学生24小时前的数据
@app.route('/stu_one_day',methods=['POST'])
def stu_one_day():
    data = request.json
    if data:
        timestamp = data['timestamp']
        name_list = data['student']
        one_dat_time = int(timestamp) - 60*60*24
        try:
            total_list = []
            for name_dic in name_list:
                name = name_dic['name']
                grade = name_dic['grade']
                stu_obj = Student.objects(name=name,grade=grade).first()
                if stu_obj:
                    all_list = []
                    stu_dic = tem_sudent(stu_obj)
                    server_list = stu_dic['server']
                    list_arr = []
                    for ip_dic in server_list:
                        # to_dic = {}
                        ip = ip_dic['host']
                        user = ip_dic['user']
                        query_res = Script.objects(user=user,net_ip=ip, timestamp__gte=one_dat_time, timestamp__lte=timestamp)
                        if query_res:
                            for res in query_res:
                                dics = tem_script(res)
                                list_arr.append(dics)
                            # print(list_arr)
                        all_list.append(list_arr)
                    stu_dic['data_info'] = all_list
                    total_list.append(stu_dic)
                else:
                    return jsonify(error_code=1, status=400, err_msg='{} or {} not exist'.format(name,grade))
            return jsonify(error_code=0, status=200, err_msg=total_list)

        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400, err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 学生对应pid查询
@app.route('/pid_sel',methods=['POST'])
def pid_sel():
    data = request.json
    if data:
        username = data['username']
        query_obj = Script.objects(user=username)
        # print(query_obj)
        if query_obj:
            list_arr = []
            for i in query_obj:
                dics = tem_scipt(i)
                list_arr.append(dics)
            return jsonify(error_code=0,status=200,err_msg=list_arr)
        else:
            return jsonify(error_code=1,status=400,err_msg='username not exist')
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 根据时间段查询记录
@app.route('/record_sel',methods=['POST'])
def record_sel():
    data = request.json
    if data:
        start_time = data['start_time']
        end_time = data['end_time']
        recor_obj = Record.objects(timestamp__gte=start_time,timestamp__lte=end_time)
        if recor_obj:
            list_attr = []
            for res in recor_obj:
                dics = {}
                dics['user'] = res.user
                dics['opera'] = res.opera
                dics['record'] = res.record
                dics['timestamp'] = res.timestamp
                list_attr.append(dics)

            return jsonify(error_code=0,status=200,err_msg=list_attr)
        else:
            return jsonify(error_code=1,status=400,err_msg='no data')

    else:
        return jsonify(error_code=1,status=400,err_msg='json error')


# 删除记录 根据user和timestamp
@app.route('/record_del',methods=['POST'])
def record_del():
    data = request.json
    if data:
        total_data = data['data_info']
        for data_obj in total_data:
            user = data_obj['username']
            timestamp = data_obj['timestamp']
            query_obj = Record.objects(user=user,timestamp=timestamp)
            if query_obj:
                query_obj.delete()
                return jsonify(error_code=0,status=200,err_msg=200)
            else:
                return jsonify(error_code=1,status=400,err_msg='no data')
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')


@app.route('/tess',methods=['POST'])
def tess():
    # data = request.json
    # host = data['host']
    data_query = Data._get_collection().aggregate([
        {"$match": {"timestamp": {"$lte": 1575189132, "$gte": 1574497932}, "net_ip": "192.168.88.91"}},
        {"$sort": {"timestamp": -1}},
        {'$unwind': '$gpu_info'},
        {"$group": {"_id": "$gpu_info.fan",
                    "gpu": {"$avg": "$gpu_info.usedMemry"},
                    "temp": {"$avg": "$gpu_info.temp"},
                    "percent": {"$avg": "$gpu_info.percent"}
                    }},
    ]
    )
    aggre_obj = list(data_query)
    if aggre_obj:
        pass
    else:
        data = Data.objects(net_ip="192.168.88.91").first()
        dicc = tem_data(data)
        dicc['diskUsage'] = 0
        dicc['UsageMemory'] = 0
        dicc['timestamp'] = 1575189132
        gpu_info = dicc['gpu_info']
        for gpu_dic in gpu_info:
            gpu_dic['gpu_mem'] = 0
            gpu_dic['usedMemry'] = 0
            gpu_dic['percent'] = 0
            gpu_dic['temp'] = 0
        print(dicc)
    return jsonify(error_msg = 200)

@app.route('/upload_tmp',methods=['POST'])
def upload_tmp():

    print("22")
    return '200'

# @app.route('/test_mo',methods=['POST'])
# def test_mo():
#
#     print("22")
#     return '200'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011,debug = True)
