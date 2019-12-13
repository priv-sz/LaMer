from pymongo import MongoClient
conn = MongoClient('127.0.0.1', 27017)
db = conn.monitor
moni_data = db.moni_data
moni_script = db.moni_script

kk = moni_data.find({'net_ip':'192.168.88.70'})
a  = list(kk)
# print(a)
for i in a:
    print(1)
    gpu_list = i['gpu_info']
    for j in gpu_list:
        j['name'] = "TITAN RTX"
        print(j['name'])
    moni_data.update(i,{'$set':{'gpu_info':gpu_list}},False,True)