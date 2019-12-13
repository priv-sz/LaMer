from flask import Flask,jsonify
from celery import Celery

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/1'

celery = Celery(app.name,broker=app.config['CELERY_BROKER_URL'],backend=app.config['CELERY_RESULT_BACKEND'])
celery.conf.update(app.config)

@celery.task
def my_back_task(arg1,arg2):
    return arg1+arg2

@app.route('/',methods=['POST'])
def index():
    my_back_task.delay(1,2)
    return jsonify(error_code=1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002,debug = True)