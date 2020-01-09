from flask import Flask,jsonify
from celery import Celery
import time
# app = Flask(__name__)
# app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/1'
#
# celery = Celery(app.name,broker=app.config['CELERY_BROKER_URL'],backend=app.config['CELERY_RESULT_BACKEND'])
# celery.conf.update(app.config)
#
# @celery.task
# def my_back_task(arg1,arg2):
#     return arg1+arg2
#
# @app.route('/',methods=['POST'])
# def index():
#     my_back_task.delay(1,2)
#     return jsonify(error_code=1)
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8002,debug = True)


# import time
# import logging
# import logging.handlers
# import datetime
# # logging初始化工作
# logging.basicConfig()
# # myapp的初始化工作
# myapp = logging.getLogger('moniserv')
# myapp.setLevel(logging.INFO)
# # 写入文件，如果文件超过100个Bytes，仅保留5个文件。
# handler = logging.handlers.RotatingFileHandler(
#     'logs/myapp.log', maxBytes=10, backupCount=10)
# logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# handler.setFormatter(logging_format)
# myapp.addHandler(handler)
#
# while True:
#     time.sleep(0.01)
#
#     myapp.info("{}".format("dsadas"))

# zeroPoint = int(time.time()) -int(time.time()-time.timezone) %86400
# now_time = time.time()
# zeroPoint = now_time - now_time % 86400 + time.timezone
#
# print(zeroPoint)
# print(time.timezone)
def ss(Student):
    kk = Student.objects.all()
    return kk