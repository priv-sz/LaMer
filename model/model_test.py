from .Model import *
import traceback


def query_all_user():
    try:
        users = Person.objects()
        print(users)
    except Exception as e:
        print('***********')
        print(e)
        traceback.print_exc()
        print('***********')


if __name__ == '__main__':
    query_all_user()