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

from flask import Flask, render_template, jsonify, make_response,current_app
from flask import request
from model.Model import *
from flask_cors import *
from utils import *

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR ='/media/DiskData/TrainServer'
root = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.debug = False
app.config['SECRET_KEY'] = 'wiwide_lma'

mongoengine.connect(db='monitor', host='127.0.0.1:27017')

# schema = graphene.Schema(query=Query, mutation=Mutation)
# app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
config_path = root + '/config/config.txt'
monit_path = root + '/monitor_ses.py'
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

# Data实例化
def tem_data(res):
    dics = {}
    dics['gpu_info'] = res.gpu_info
    dics['dislUsage'] = res.diskUsage
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
    dics['username'] = res.username
    dics['gender'] = res.gender
    dics['server'] = res.server
    dics['img_addr'] = res.img_addr
    dics['github'] = res.github
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
        if "time" not in data:
            data['time'] = 1800
        timestamp = time.time()
        try:
            with open(config_path, 'r') as conf:
                txt_file = conf.readlines()
            ip_list = []
            for dics in txt_file:
                dicc = eval(dics)
                ip_list.append(dicc['host'])
            if data['host'] in ip_list:
                return jsonify(error_code=1, status=400,err_msg='ip is exist')
            else:
                with open(config_path, 'a+') as conf:
                    conf.write(str(data) + '\n')
                run_data(data['host'])
                time.sleep(1.5)
                query_obj = Record(user=data['host'], opera="add_server", record=data, timestamp=int(timestamp))
                query_obj.save()
                # 从data查询数据
                query_oo = Data.objects(net_ip=data['host']).order_by('-timestamp').limit(1)
                if query_oo:
                    list_at = []
                    for res in query_oo:
                        data = tem_data(res)
                        list_at.append(data)
                    return jsonify(error_code=0, status=200, err_msg=list_at)
                else:
                    return jsonify(error_code=0, status=200, err_msg=[])

        except Exception as e:
            print(e)
            ip = data['host']
            with open(config_path, 'r') as conf:
                txt_conf = conf.readlines()
            list_arr = []
            for i in txt_conf:
                confs = eval(i)
                list_arr.append(confs['host'])
            if ip in list_arr:
                with open(config_path, 'w') as conf:
                    for value in txt_conf:
                        con_obj = eval(value)
                        if ip == con_obj['host']:
                            continue
                        conf.write(value)
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
            for i in txt_conf:
                dic_ = eval(i)
                ip_list.append(dic_['host'])
            if old_ip in ip_list:
                with open(config_path,'w')as f:
                    new_data['user'] = "user"
                    new_data['pwd'] = "priv123"
                    for value in txt_conf:
                        dic_obj = eval(value)
                        if old_ip == dic_obj['host']:
                            f.write(str(new_data)+'\n')
                        else:
                            f.write(value)

                run_data(new_data['host'])
                time.sleep(1.5)
                query_obj = Record(user=new_data['host'], opera="edi_server", record=data, timestamp=int(timestamp))
                query_obj.save()
                if old_ip != new_data['host']:
                    Data.objects(net_ip=old_ip).update(set__net_ip=new_data)
                    Student.objects(net_ip=old_ip).update(set__net_ip=new_data)

                query_oo = Data.objects(net_ip=new_data['host']).order_by('-timestamp').limit(1)
                list_at = []
                if query_oo:
                    for res in query_oo:
                        data = tem_data(res)
                        list_at.append(data)

                return jsonify(error_code=0, status=200,err_msg=list_at)
            else:
                return jsonify(error_code=1,status=400,err_msg='ip not exist')

        except Exception as e:
            print(e)
            ip = new_data['host']
            with open(config_path, 'r') as conf:
                txt_conf = conf.readlines()
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
                del_data(ip)
                with open(config_path,'w') as conf:
                    for value in txt_conf:
                        con_obj = eval(value)
                        if ip == con_obj['host']:
                            continue
                        conf.write(value)
                rec_obj = Record(user=ip, opera='del_server', record=data, timestamp=int(timestamp))
                rec_obj.save()
                query_obj = Student.objects(server=ip)
                if query_obj:
                    query_obj.delete()
                quer_obj = Data.objects(net_ip=ip)
                if quer_obj:
                    quer_obj.delete()
                que_obj = Script.objects(net_ip=ip)
                if que_obj:
                    que_obj.delete()

                return jsonify(error_code=0,status=200,err_msg=200)
            else:
                return jsonify(error_code=1,status=400,err_msg='ip not exist')
        except Exception as e:
            print(e)
            ip_list = []
            host  = ''
            for dics in txt_file:
                dicc = eval(dics)
                if data['host'] == dicc['host']:
                    host = dics
                ip_list.append(dicc['host'])
            if host:
                with open(config_path, 'a+') as conf:
                    conf.write(str(host) + '\n')
            return jsonify(error_code=1,status=400,err_msg=e)

    else:
        return jsonify(error_code=1,err_msg='json error')

# 通过ip查找对应name
def ip_find(conf_obj,ip):
    for i in conf_obj:
        dic_ob = eval(i)
        if dic_ob['host']==ip:
            name = dic_ob['name']
            return name

# 查询所有服务器信息
@app.route('/all_server',methods=['POST'])
def all_server():
    query_all = Data.objects.all()
    try:
        if query_all:
            with open(config_path, 'r') as conf:
                conf_obj = conf.readlines()
            ip_list = []
            for i in conf_obj:
                dic_ = eval(i)
                ip_list.append(dic_['host'])
            list_arr = []
            for ip in ip_list:
                query_res = Data.objects(net_ip=ip).order_by('-timestamp').limit(1)
                to_dic = {}
                if query_res:
                    data_list = []
                    for obj in query_res:
                        dics = tem_data(obj)
                        data_list.append(dics)
                    to_dic['name'] = ip_find(conf_obj, ip)
                    to_dic['ip'] = ip
                    to_dic['data_info'] = data_list
                    list_arr.append(to_dic)
                else:
                    to_dic['name'] = ip_find(conf_obj, ip)
                    to_dic['ip'] = ip
                    to_dic['data_info'] = []
                    list_arr.append(to_dic)

            return jsonify(error_code=0,status=200,err_msg=list_arr)
        else:
            return jsonify(error_code=0,status=200,err_msg=[])
    except Exception as e:
        print(e)
        return jsonify(error_code=1,status=400,err_msg=e)

# 根据时间段筛选数据
@app.route('/period_time',methods=['POST'])
def monitor():
    data = request.json
    if data:
        start_time = data['start_time']
        end_time = data['end_time']
        ip_list = data['ip_list']
        with open(config_path, 'r') as conf:
            conf_obj = conf.readlines()
        try:
            if len(ip_list)>=1:

                all_list = []
                for ip in ip_list:
                    to_dic = {}
                    list_arr = []
                    query_res = Data.objects(net_ip=ip,timestamp__gte=start_time,timestamp__lte=end_time)
                    for res in query_res:
                        dics = tem_data(res)
                        list_arr.append(dics)
                    # print(list_arr)
                    to_dic['name'] = ip_find(conf_obj,ip)
                    to_dic['ip'] = ip
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

# 根据固定时间筛选
@app.route('/fixed_time',methods=['POST'])
def fixed_time():
    data = request.json
    if data:
        timestamp = data['timestamp']
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
                            to_dic['name'] = ip_find(conf_obj, ip)
                            to_dic['ip'] = ip
                            to_dic['data_info'] = dics
                            list_attr.append(to_dic)

                        else:
                            dics = tem_data(on_a[0])
                            to_dic['name'] = ip_find(conf_obj, ip)
                            to_dic['ip'] = ip
                            to_dic['data_info'] = dics
                            list_attr.append(to_dic)
                    else:
                        dict = {"ip":ip,"data_info":{}}
                        dict['name'] = ip_find(conf_obj, ip)
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
        timestamp = data['timestamp']
        ip_list = data['ip_list']
        with open(config_path, 'r') as conf:
            conf_obj = conf.readlines()
        dateArray = datetime.datetime.utcfromtimestamp(timestamp)
        dateStr = (dateArray + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
        timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        one_dat_time = int(time.mktime(timeArray))
        try:
            if len(ip_list)>=1:

                all_list = []
                for ip in ip_list:
                    to_dic = {}
                    list_arr = []
                    query_res = Data.objects(net_ip=ip,timestamp__gte=one_dat_time,timestamp__lte=timestamp)
                    for res in query_res:
                        dics = tem_data(res)
                        list_arr.append(dics)
                    # print(list_arr)
                    to_dic['name'] = ip_find(conf_obj, ip)
                    to_dic['ip'] = ip
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

def img_pat():
    uuid_str = uuid.uuid4().hex
    img_path = IMG_PATH + uuid_str + '.jpg'
    if os.path.exists(img_path):
        img_pat()
    else:
        return img_path


# 学生添加
# TODO 图片存储
@app.route('/stu_add',methods=['POST'])
def student_add():
    data = request.json
    timestamp = time.time()
    if data:
        username = data['username']
        gender = data['gender']
        server = data['server']
        img_addr = data['img_addr']
        github = data['github']
        grade = data['grade']
        phone = data['phone']
        # 图片处理
        try:
            query_obj = Student.objects(username=username,grade=grade)
            if query_obj:
                return jsonify(error_code=1,status=400,err_msg='username is exist')
            else:
                if img_addr:
                    img_addr = ''.join(img_addr.split(',')[1:])
                    print(img_addr)
                    imagedata = base64.b64decode(img_addr)
                    img_path = img_pat()
                    with open(img_path,'wb') as f:
                        f.write(imagedata)
                    img_addr = '/static/upload/'+img_path.split('/')[-1]
                else:
                    img_addr = ""
                post_obj = Student(username=username, gender=gender, server=server, img_addr=img_addr, github=github,grade=grade,phone=phone)
                post_obj.save()
                rec_obj = Record(user=username,opera='add',record=data,timestamp=int(timestamp))
                rec_obj.save()
                return jsonify(error_code=0, err_msg=200)
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
        username_list = data['username']
        grade = data['grade']
        try:
            for username in username_list:
                query_obj = Student.objects(username=username,grade=grade)
                if query_obj:
                    query_ob = Script(user=username)
                    if query_ob:
                        query_ob.delete()
                    query_obj.delete()
                    rec_obj = Record(user=username,opera='del',record=data,timestamp=int(timestamp))
                    rec_obj.save()
                    return jsonify(error_code=0,status=200,err_msg=200)
                else:
                    return jsonify(error_code=1,status=400,err_msg='username not exist')
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)

    else:
        return jsonify(error_code=1,status=400,err_msg='json error')
# 学生编辑
# 改什么传什么，列表将原来未修改的值带上
@app.route('/stu_edi',methods=['POST'])
def student_edi():
    data = request.json
    timestamp = time.time()
    record_data = copy.copy(data)
    if data:
        old_data = data['old_data']
        new_data = data['new_data']
        username = old_data['username']
        grade = old_data['grade']
        try:
            query_obj = Student.objects(username=username,grade=grade).first()
            if query_obj:
                #
                if 'username' in new_data:
                    Script.objects(user=username).update(set__user=new_data['username'])
                for key,value in new_data.items():
                    setattr(query_obj,key,value)
                query_obj.save()
                rec_obj = Record(user=username, opera='upd', record=record_data, timestamp=int(timestamp))
                rec_obj.save()
                return jsonify(error_code=0,status=200,err_msg=200)
            else:
                return jsonify(error_code=1,status=400,err_msg='username not exist')

        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')



# 所有学生查询
@app.route('/stu_sel',methods=['POST'])
def student_sel():
    timestamp = time.time()
    dateArray = datetime.datetime.utcfromtimestamp(timestamp)
    dateStr = (dateArray + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
    timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
    one_dat_time = int(time.mktime(timeArray))
    query_set = Student.objects.all()
    if query_set:
        try:
            list_arr = []
            for stu in query_set:

                query_obj = tem_sudent(stu)
                username = stu.username
                # 从小到大
                query_scipt = Script.objects.filter(user=username,timestamp__gte=one_dat_time,timestamp__lte=timestamp).order_by("timestamp")
                data_list = []
                if query_scipt:
                    for scr in query_scipt:
                        scrip_dic = tem_script(scr)
                        data_list.append(scrip_dic)
                    query_obj['data_info'] = data_list
                    list_arr.append(query_obj)
                else:
                    query_obj['data_info'] = []
                    list_arr.append(query_obj)

            return jsonify(error_code=0,status=200,err_msg=list_arr)
        except Exception as e:
            print(e)
            return jsonify(error_code=1,status=400,err_msg=e)
    else:
        return jsonify(error_code=1,status=400,err_msg='no data')

# 学生根据时间段查询
# TODO 对时间进行拆分7天获取7条数据
@app.route('/stu_period_time',methods=['POST'])
def stu_period_time():
    data = request.json
    if data:
        start_time = data['start_time']
        end_time = data['end_time']
        user_list = data['username']
        # end = datetime.datetime.fromtimestamp(end_time)
        # time_diffe = (end - start).days
        list_all = []
        for user in user_list:
            for i in range(7):
                start = datetime.datetime.fromtimestamp(start_time)
                destarr = (start + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
                timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                Yestarday = int(time.mktime(timeArray))
                aggre_obj = Script._get_collection().aggregate([
                    {"$match": {"timestamp": {"$lte": start_time,"$gte":Yestarday},"user":user}},
                    {"$sort": {"timestamp": -1}},
                    {"$group": {"_id": "$user",
                                "timestamp": {"$first": "$timestamp"},
                                "net_ip":{"$first":"$net_ip"},
                                "gpu_pid":{"$first":"$gpu_pid"},
                                "start_time":{"$first":"$start_time"},
                                "config":{"$first":"$config"},
                                "duration":{"$first":"$duration"},
                                "gpu_use":{"$first":"$gpu_use"},
                                "gpu_mem": {"$avg": "$gpu_mem"}
                                }},
                     ]
                )
                list_attr = []
                aggre_obj = list(aggre_obj)
                if aggre_obj:
                    for agg_con in aggre_obj:
                        agg_con['user'] = agg_con.pop("_id")
                        list_attr.append(agg_con)
                else:
                    dics = {}
                    list_attr.append(dics)
                start = datetime.datetime.fromtimestamp(start_time)
                destarr = (start + datetime.timedelta(days=+1)).strftime("%Y-%m-%d %H:%M:%S")
                timeArray = time.strptime(destarr, "%Y-%m-%d %H:%M:%S")
                start_time = int(time.mktime(timeArray))
                dic_one = {}
                dic_one['user'] = user
                dic_one['data_info'] = list_attr
                list_all.append(dic_one)
        return jsonify(error_code=0,status=200,err_msg=list_all)
    else:
        return jsonify(error_code=1,status=400,err_msg='json error')

# 学生根据最近时间进行查询
@app.route('/stu_fixed_time',methods=['POST'])
def stu_fixed_time():
    data = request.json
    if data:
        try:
            timestamp = data['timestamp']
            name_list = data['username']
            list_attr = []
            for username in name_list:
                on_a = Script.objects.filter(user=username, timestamp__lte=timestamp).order_by("-timestamp").limit(1)
                next_a = Script.objects.filter(user=username, timestamp__gte=timestamp).order_by("timestamp").limit(1)
                to_dic = {}
                if on_a and next_a:
                    if timestamp - on_a[0].timestamp > timestamp - next_a[0].timestamp:
                        dics = tem_script(next_a[0])
                        to_dic['name'] = username
                        to_dic['data_info'] = dics
                        list_attr.append(to_dic)

                    else:
                        dics = tem_script(on_a[0])
                        to_dic['name'] = username
                        to_dic['data_info'] = dics
                        list_attr.append(to_dic)
                else:
                    dict = {}
                    dict['name'] = username
                    dict['data_info'] = []
                    list_attr.append(dict)
            return jsonify(error_code=0,status=200,err_msg=list_attr)
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
        name_list = data['username']
        dateArray = datetime.datetime.utcfromtimestamp(timestamp)
        dateStr = (dateArray + datetime.timedelta(days=-1)).strftime("%Y-%m-%d %H:%M:%S")
        timeArray = time.strptime(dateStr, "%Y-%m-%d %H:%M:%S")
        one_dat_time = int(time.mktime(timeArray))
        try:

            all_list = []
            for user in name_list:
                to_dic = {}
                list_arr = []
                query_res = Script.objects(user=user, timestamp__gte=one_dat_time, timestamp__lte=timestamp)
                if query_res:
                    for res in query_res:
                        dics = tem_script(res)
                        list_arr.append(dics)
                    # print(list_arr)
                    to_dic['name'] = user
                    to_dic['data_info'] = list_arr
                    all_list.append(to_dic)
                else:
                    to_dic['name'] = user
                    to_dic['data_info'] = []
                    all_list.append(to_dic)
            return jsonify(error_code=0, status=200,err_msg=all_list)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9000,debug = True)
