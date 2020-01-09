from .db import *


# 记录硬件信息
class Data(db_eng.Document):
    meta = {
        'collection':'moni_data'
    }
    diskUsage = db_eng.IntField()
    # gpu_version = db_eng.StringField()
    cpuUsagePercent = db_eng.IntField()
    gpu_info = db_eng.ListField()
    net_num = db_eng.IntField()
    cpu_model = db_eng.StringField()
    TotalMemory = db_eng.IntField()
    cpu_num = db_eng.IntField()
    # pid_mess = db_eng.DictField()
    # gpu_num = db_eng.IntField()
    net_ip = db_eng.StringField()
    timestamp = db_eng.IntField()
    UsageMemory = db_eng.IntField()
    # gpu_temperat = db_eng.DictField()
    diskTotal = db_eng.IntField()

# 记录pid的信息
class Script(db_eng.Document):
    meta = {
        'collection':'moni_script'
    }

    user = db_eng.StringField()
    gpu_pid = db_eng.StringField()
    start_time = db_eng.StringField()
    gpu_mem = db_eng.IntField()
    config = db_eng.StringField()
    duration = db_eng.StringField()
    gpu_use =db_eng.IntField()
    net_ip = db_eng.StringField()
    timestamp = db_eng.IntField()

# 记录学生信息
class Student(db_eng.Document):
    meta = {
        'collection':'moni_student'
    }

    name = db_eng.StringField()
    # 0男1女
    gender = db_eng.IntField()
    server = db_eng.ListField()
    img_addr = db_eng.StringField()
    github = db_eng.StringField()
    grade = db_eng.IntField()
    phone = db_eng.IntField()
    stuid = db_eng.IntField()
    cardid = db_eng.IntField()

    email = db_eng.StringField()
    # 民族
    nation = db_eng.StringField()
    hometown = db_eng.StringField()
    # 政治面貌,党派
    parties = db_eng.StringField()
    birthday = db_eng.IntField()
    married = db_eng.StringField()
    # 教育经历
    educationExperience = db_eng.ListField()
    # 实习
    practice = db_eng.StringField()
    # 技能
    skill = db_eng.StringField()
    # 奖项
    awards = db_eng.StringField()
    # 自我评价
    evaluation = db_eng.StringField()



# 记录增删改查的记录
class Record(db_eng.Document):
    meta = {
        'collection': 'moni_record'
    }

    user = db_eng.StringField()
    opera = db_eng.StringField()
    record = db_eng.DictField()
    timestamp = db_eng.IntField()

# 记录登录信息
class Person(db_eng.Document):
    meta = {
        'collection': 'moni_person'
    }

    name = db_eng.StringField()
    password = db_eng.StringField()
    auth = db_eng.IntField(default=1)
    img_addr = db_eng.StringField()

# 记录硬件信息 测试
class DataC(db_eng.Document):
    meta = {
        'collection':'moni_ceshi'
    }
    diskUsage = db_eng.IntField()
    # gpu_version = db_eng.StringField()
    cpuUsagePercent = db_eng.IntField()
    gpu_info = db_eng.ListField()
    net_num = db_eng.IntField()
    cpu_model = db_eng.StringField()
    TotalMemory = db_eng.IntField()
    cpu_num = db_eng.IntField()
    # pid_mess = db_eng.DictField()
    # gpu_num = db_eng.IntField()
    net_ip = db_eng.StringField()
    timestamp = db_eng.IntField()
    UsageMemory = db_eng.IntField()
    # gpu_temperat = db_eng.DictField()
    diskTotal = db_eng.IntField()


# 自定义函数
# 序列化处理，排除指定字段
def m2d_exclude(obj, _id='_id', *args):
    model_dict = obj.to_mongo().to_dict()
    if _id:
        list(map(model_dict.pop, [_id]))
    if args:
        list(map(model_dict.pop, list(args)))
    if "_id" in model_dict.keys():
        model_dict["_id"] = str(model_dict["_id"])
    return model_dict
