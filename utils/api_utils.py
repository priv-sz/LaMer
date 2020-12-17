import time
import datetime


def float2int(x):
    for key, value in x.items():
        if type(value) == float:
            x[key] = int(value)
    return x


def get_week():
    now_time = int(time.time())
    timeArray = time.localtime(now_time)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    now_date = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    loop_count = now_date.hour
    week_now = now_date.weekday()
    print(loop_count)

    # 正序
    time_gte = now_date - datetime.timedelta(days=week_now, hours=loop_count, minutes=now_date.minute, seconds=now_date.second)
    timestamp_gte = int(time.mktime(time_gte.timetuple()))
    timestamp_lte = timestamp_gte + 3600 * 24 * 7
    time_lte = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_lte))
    return timestamp_gte, timestamp_lte


def get_today_time():
    now_time = int(time.time())
    timeArray = time.localtime(now_time)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    now_date = datetime.datetime.strptime(otherStyleTime, "%Y-%m-%d %H:%M:%S")
    loop_count = now_date.hour
    print(loop_count)

    # 正序
    time_gte = now_date - datetime.timedelta(hours=loop_count, minutes=now_date.minute,
                                             seconds=now_date.second)
    timestamp_gte = int(time.mktime(time_gte.timetuple()))
    timestamp_lte = now_time + 30*60
    time_lte = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp_lte))
    return timestamp_gte, timestamp_lte