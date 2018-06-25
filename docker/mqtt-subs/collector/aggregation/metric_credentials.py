# Query untuk mendapatkan Metrics Credentials untuk username dan password

from pymongo import MongoClient
import time
from datetime import datetime, timedelta
mongoconn = MongoClient('mongodb://192.168.1.100:27017/')
db = mongoconn.fipro
start_ts = time.time()

# Username Aggregator
db.logs.aggregate([
    {
        "$match":
        {
            "identifier": "fb0963921f12",
            "$and": [ {"username": {"$ne": None} }, {"username": {"$ne": ""}} ]
        }
    },
    {
        "$group":
        {
            "_id": "$username",
            "counts": {"$sum": 1}  
        }
    },
    {
        "$sort":{"counts": -1}
    },
    {
        "$out": "honeypot_top10_username_credential_metric"
    }
])

# Password Aggregator
db.logs.aggregate([
    {
        "$match":
        {
            "identifier": "fb0963921f12",
            "$and": [ {"password": {"$ne": None} }, {"password": {"$ne": ""}} ]
        }
    },
    {
        "$group":
        {
            "_id": "$password",
            "counts": {"$sum": 1}  
        }
    },
    {
        "$sort":{"counts": -1}
    },
    {
        "$out": "honeypot_top10_password_credential_metric"
    }
])

end_ts = time.time()
print (end_ts - start_ts)