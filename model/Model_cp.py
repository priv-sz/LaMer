from .db import db_eng as db

# 记录硬件信息
class Data(db.Document):
    meta = {
        'collection':'moni_data'
    }
    diskUsage = db.IntField()
    # gpu_version = StringField()
    cpuUsagePercent = db.IntField()
    gpu_info = db.ListField()
    net_num = db.IntField()
    cpu_model = db.StringField()
    TotalMemory = db.IntField()
    cpu_num = db.IntField()
    # pid_mess = DictField()
    # gpu_num = IntField()
    net_ip = db.StringField()
    timestamp = db.IntField()
    UsageMemory = db.IntField()
    # gpu_temperat = DictField()
    diskTotal = db.IntField()

# 记录pid的信息
class Script(db.Document):
    meta = {
        'collection':'moni_script'
    }

    user = db.StringField()
    gpu_pid = db.StringField()
    start_time = db.StringField()
    gpu_mem = db.IntField()
    config = db.StringField()
    duration = db.StringField()
    gpu_use = db.IntField()
    net_ip = db.StringField()
    timestamp = db.IntField()

# 记录pid的信息
class ScriptS(db.Document):
    meta = {
        'collection':'moni_script_copy'
    }

    user = db.StringField()
    gpu_pid = db.StringField()
    start_time = db.StringField()
    gpu_mem = db.IntField()
    config = db.StringField()
    duration = db.StringField()
    gpu_use = db.IntField()
    net_ip = db.StringField()
    timestamp = db.IntField()

# 记录学生信息
class Student(db.Document):
    meta = {
        'collection':'moni_student'
    }

    name = db.StringField()
    # 0男1女
    gender = db.IntField()
    server = db.ListField()
    img_addr = db.StringField()
    github = db.StringField()
    grade = db.IntField()
    phone = db.IntField()
    stuid = db.IntField()
    cardid = db.IntField()

# 记录学生信息
class StudentS(db.Document):
    meta = {
        'collection':'moni_student_copy'
    }

    name = db.StringField()
    # 0男1女
    gender = db.IntField()
    server = db.ListField()
    img_addr = db.StringField()
    github = db.StringField()
    grade = db.IntField()
    phone = db.IntField()
    stuid = db.IntField()
    cardid = db.IntField()


# 记录增删改查的记录
class Record(db.Document):
    meta = {
        'collection': 'moni_record'
    }

    user = db.StringField()
    opera = db.StringField()
    record = db.DictField()
    timestamp = db.IntField()

# 记录登录信息
class Person(db.Document):
    meta = {
        'collection': 'moni_person'
    }

    name = db.StringField()
    password = db.StringField()
    auth = db.IntField(default=1)


# 记录硬件信息 测试
class DataD(db.Document):
    meta = {
        'collection':'moni_data_copy'
    }
    diskUsage = db.IntField()
    # gpu_version = StringField()
    cpuUsagePercent = db.IntField()
    gpu_info = db.ListField()
    net_num = db.IntField()
    cpu_model = db.StringField()
    TotalMemory = db.IntField()
    cpu_num = db.IntField()
    # pid_mess = DictField()
    # gpu_num = IntField()
    net_ip = db.StringField()
    timestamp = db.IntField()
    UsageMemory = db.IntField()
    # gpu_temperat = DictField()
    diskTotal = db.IntField()