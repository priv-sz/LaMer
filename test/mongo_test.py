from model.Model import *
import traceback
import mongoengine
mongoengine.connect(db='monitor_copy', host='192.168.88.191:27017')
# mongoengine.connect(db='monitor_copy', host='140.143.137.79:27108')


def query_all_user():
    try:
        users = Person.objects()
        users = list(map(lambda x: m2d_exclude(x, '_id', "password"), users))
        print(users)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')


def update_user(userName, **args):
    try:
        user = Person.objects(name=userName).first()
        for i in args:
            print("{} -- {}".format(i, args[i]))
            setattr(user, i, args[i])
        user.save()
        print(m2d_exclude(user))
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')


def query_server(ip):
    query_res = Data.objects(net_ip=ip).order_by('-timestamp').first()
    if query_res:
        print(m2d_exclude(query_res))
    else:
        print('无 ip = {}'.format(ip))


if __name__ == '__main__':
    # query_all_user()
    # update_user('tf', name='ls')
    query_server(ip="192.168.88.191")