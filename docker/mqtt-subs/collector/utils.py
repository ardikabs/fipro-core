

import datetime
import pytz

def get_datetime(timestamp):
    utctime = datetime.datetime.fromtimestamp(float(timestamp), tz=pytz.utc)
    return utctime.astimezone(pytz.timezone('Asia/Jakarta'))

def get_date_str(timestamp):
    return get_datetime(timestamp).strftime('%Y-%m-%d')

def get_date(timestamp):
    return datetime.datetime.strptime(get_date_str(timestamp), "%Y-%m-%d")

def get_hour(timestamp):
    return get_datetime(timestamp).strftime("%H")

def get_year(timestamp):
    return get_datetime(timestamp).strftime("%Y")