import os
import paramiko
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 删除 70 服务器, 手动修改
config_path = BASE_DIR+'/test/config.txt'
# local_file = BASE_DIR + '/remote_files/monitor_perf.py'
local_file = BASE_DIR + '/remote_files/requirements.txt'
# local_file = BASE_DIR + '/scripts/generate_database_json.py'
remote_dir = "/home/user/Monitor_script/"
# remote_file = "/home/user/Monitor_script/monitor_perf_cc.py"
# remote_file = "/home/user/Monitor_script/monitor_perf.py"
remote_file = "/home/user/Monitor_script/requirements.txt"
# remote_file = "/home/user/Monitor_script/generate_database_json.py"

def copy_monitor_per():
    with open(config_path, 'r') as f:
        conf = f.readlines()
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for dics in conf:
        try:
            dicc = eval(dics)
            host = dicc['host']
            user = dicc['user']
            pwd = dicc['pwd']
            print(host)
            ssh = paramiko.Transport((host, 22))
            cmd = 'ls {}'.format(remote_dir)
            client.connect(host, 22, username=user, password=pwd, timeout=3)
            sdtin, stdout, stderr = client.exec_command(cmd)
            if stdout.readline() != '':
                print("exist")
            else:
                print("not exist")
                cmd = 'mkdir {}'.format(remote_dir)
                client.exec_command(cmd)
            ssh.connect(username=user, password=pwd)
            sftp = paramiko.SFTPClient.from_transport(ssh)
            sftp.put(local_file, remote_file)
            ssh.close()


            _, stdout1, stderr1 = client.exec_command(
                'echo priv123 | sudo -S pip3 install -r {} -i https://pypi.tuna.tsinghua.edu.cn/simple'.format(
                    remote_file))
            stdout1.read().decode('utf-8')
        except Exception as e:
            print('***********')
            print(host)
            print(e)
            traceback.print_exc()
            print('***********')


if __name__ == '__main__':
    copy_monitor_per()