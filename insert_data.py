import os
from pymongo import MongoClient
import datetime,random

conn = MongoClient('127.0.0.1', 27017)
db = conn.monitor_copy
moni_ceshi = db.moni_ceshi

def randomtimes(start, end, n):
    # stime = datetime.datetime.strptime(start, frmt)
    # etime = datetime.datetime.strptime(end, frmt)
    return [int(random.random() * (end - start) + start) for _ in range(n)]

def run():
    time_list = randomtimes(1576462067,1577066867,5)

    for timestamp in time_list:
        dics = {
            "TotalMemory": 31,
            "UsageMemory": 8,
            "cpuUsagePercent": 487,
            "cpu_model": "Intel(R) Core(TM) i7-7800X CPU @ 3.50GHz",
            "cpu_num": 12,
            "diskTotal": 197,
            "diskUsage": 21,
            "gpu_info": [
                {
                    "fan": 0,
                    "name": "TITAN Xp COLLECTORS EDITION",
                    "percent": 26.0,
                    "power": "82W/250W",
                    "script": [
                        {
                            "config": "cfgs/semseg/ade20k/R-18-dilated_ppm.yaml",
                            "duration": "4:11",
                            "gpu_mem": 2023,
                            "gpu_pid": "13851",
                            "gpu_use": 0,
                            "net_ip": "192.168.88.91",
                            "start_time": "23:37",
                            "timestamp": 1576424541,
                            "user": "user"
                        },
                        {
                            "config": "so_c.py",
                            "duration": "9876:42",
                            "gpu_mem": 1139,
                            "gpu_pid": "18674",
                            "gpu_use": 0,
                            "net_ip": "192.168.88.91",
                            "start_time": "12月13",
                            "timestamp": 1576424541,
                            "user": "user"
                        }
                    ],
                    "temp": 64,
                    "totalMemry": 12788498432,
                    "usedMemry": 0,
                    "version": "10.410.48"
                },
                {
                    "fan": 1,
                    "name": "TITAN Xp COLLECTORS EDITION",
                    "percent": 0.1,
                    "power": "18W/250W",
                    "script": [],
                    "temp": 51,
                    "totalMemry": 12787122176,
                    "usedMemry": 0,
                    "version": "10.410.48"
                }
            ],
            "net_num": 1,
            "timestamp": 1576424541,
            "net_ip":"192.168.88.91"
        }
        dics['timestamp'] = timestamp
        moni_ceshi.insert(dics)


if __name__ == '__main__':
    run()