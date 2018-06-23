

import datetime
from pytz import timezone

def get_datetime(timestamp):
    return datetime.datetime.fromtimestamp(float(timestamp), tz=timezone('Asia/Jakarta'))

def get_date_str(timestamp):
    return get_datetime(timestamp).strftime('%Y-%m-%d')

def get_date(timestamp):
    return datetime.datetime.strptime(get_date_str(timestamp), "%Y-%m-%d")

def get_hour(timestamp):
    return get_datetime(timestamp).hour

def get_year(timestamp):
    return get_datetime(timestamp).year