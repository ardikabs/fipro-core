from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate_event = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-206189149201",
            "geoip": {"$ne": None}
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
        "$out": "honeypot_source_ip"
    }
])
end_ts = time.time()
print (end_ts - start_ts)