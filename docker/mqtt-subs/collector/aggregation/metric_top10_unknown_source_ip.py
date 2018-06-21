from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://192.168.72.128:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate_event = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-19216872129",
            "geoip": {"$eq": None}
        }
    },

    {
        "$group": {
            "_id": {
                "src_ip": "$src_ip",
            },
            "count": {"$sum": 1}
        }
    },

    {
        "$project":{
            "_id": 0,
            "src_ip": "$_id.src_ip",
            "count": 1
        }
    },
    {
        "$sort": { "count": -1}
    },
    {
        "$limit": 10
    },
    {
        "$out": "honeypot_top10_unkown_source_ip_metric"
    }
])
end_ts = time.time()
print (end_ts - start_ts)