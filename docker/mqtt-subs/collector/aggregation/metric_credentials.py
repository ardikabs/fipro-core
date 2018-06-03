# Query untuk mendapatkan Metrics Credentials untuk username dan password

from pymongo import MongoClient
import time
from datetime import datetime, timedelta
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()

# Username Aggregator
db.logs.aggregate([
    {
        "$match":
        {
            "identifier": "5c3669d44b6a",
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
        "$limit": 10
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
            "identifier": "5c3669d44b6a",
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
        "$limit": 10
    },
    {
        "$out": "honeypot_top10_password_credential_metric"
    }
])

end_ts = time.time()
print (end_ts - start_ts)