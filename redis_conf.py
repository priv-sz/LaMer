import redis
import paramiko
import threading
#
# from multiprocessing import Pool
# import time
# def worker(x):
#     while 1:
#         print(x)
#         if x ==1:
#             break
#         time.sleep(30)
#
# pool = Pool(1) # run 3 process simultaneously
# # for i in range(1, 11):
# #     print(i)
# pool.apply_async(worker, (2,))
#
# print("---start---")
# pool.close() # 关闭进程池，不允许继续添加进程
# # 等待进程池中的所有进程结束
# print("---end---")

def sta():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect("192.168.88.111", 22, username="user", password="priv123", timeout=4)
    # print(dir_path+'/monitor_perf.py')
    cmd0 = "ps -ef | grep monitor_perf.py | grep -v grep | awk '{print $2}' | xargs kill -15"
    stdin, stdout, stderr = client.exec_command(cmd0)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    client.connect("192.168.88.111", 22, username="user", password="priv123", timeout=4)
    cmd = 'python3 /home/user/Program/ws/monitor_web/monitor_perf.py'
    stdin1, stdout1, stderr1 = client.exec_command(cmd)

# def redis_notify_del():
#     global redis_conn
#     global config_yaml
#     print('multi config redis start work')
#     try:
#         sub_strict = redis.StrictRedis('127.0.0.1', 6379).pubsub()
#         sub_strict.subscribe('del_config')
#         for i in sub_strict.listen():
#             if isinstance(i.get('data'), bytes):
#                 redis_data = i.get('data').decode()
#                 # if redis_data == 'exit':
#                 # 	# worker退出的过程中将无法响应其他数据修改请求
#                 #     print('Gearman monitor receive restart signal.')
#                 #     redis_continue_work = False
#                 #     sub_strict.unsubscribe('config')
#                 #     break
#                 if redis_data:
#                     # print(redis_data)
#                     # file_name = eval(redis_data)
#                     sta()
#
#     except Exception as e:
#         print(e)

if __name__ == '__main__':
    # kk = threading.Thread(target=redis_notify_del)
    # kk.start()
    sta()