

import datetime

def get_date(timestamp):
    return datetime.datetime.fromtimestamp(float(timestamp)).strftime("%Y%m%d")

def get_hour(timestamp):
    return datetime.datetime.fromtimestamp(float(timestamp)).strftime("%H")
