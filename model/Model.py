from mongoengine import *

# 记录硬件信息
class Data(Document):
    meta = {
        'collection':'moni_data'
    }
    diskUsage = IntField()
    # gpu_version = StringField()
    cpuUsagePercent = IntField()
    gpu_info = ListField()
    net_num = IntField()
    cpu_model = StringField()
    TotalMemory = IntField()
    cpu_num = IntField()
    # pid_mess = DictField()
    # gpu_num = IntField()
    net_ip = StringField()
    timestamp = IntField()
    UsageMemory = IntField()
    # gpu_temperat = DictField()
    diskTotal = IntField()

# 记录pid的信息
class Script(Document):
    meta = {
        'collection':'moni_script'
    }

    user = StringField()
    gpu_pid = StringField()
    start_time = StringField()
    gpu_mem = IntField()
    config = StringField()
    duration = StringField()
    gpu_use =IntField()
    net_ip = StringField()
    timestamp = IntField()

# 记录学生信息
class Student(Document):
    meta = {
        'collection':'moni_student'
    }

    name = StringField()
    # 0男1女
    gender = IntField()
    server = ListField()
    img_addr = StringField()
    github = StringField()
    grade = IntField()
    phone = IntField()
    stuid = IntField()
    cardid = IntField()


# 记录增删改查的记录
class Record(Document):
    meta = {
        'collection': 'moni_record'
    }

    user = StringField()
    opera = StringField()
    record = DictField()
    timestamp = IntField()

# 记录登录信息
class Person(Document):
    meta = {
        'collection': 'moni_person'
    }

    name = StringField()
    password = StringField()
    auth = IntField(default=1)


# 记录硬件信息 测试
class DataC(Document):
    meta = {
        'collection':'moni_ceshi'
    }
    diskUsage = IntField()
    # gpu_version = StringField()
    cpuUsagePercent = IntField()
    gpu_info = ListField()
    net_num = IntField()
    cpu_model = StringField()
    TotalMemory = IntField()
    cpu_num = IntField()
    # pid_mess = DictField()
    # gpu_num = IntField()
    net_ip = StringField()
    timestamp = IntField()
    UsageMemory = IntField()
    # gpu_temperat = DictField()
    diskTotal = IntField()