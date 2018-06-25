
# Query untuk mendapatkan Data Metrics Destination Ports
# berdasarkan waktu

from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://192.168.1.100:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate = db.logs.aggregate([
    {
        "$match": {
            "identifier": "fb0963921f12",
            "dst_port": {"$ne": None},
            "timestamp": {"$gte": datetime.datetime.today() - datetime.timedelta(weeks=102) }
        }
    },

    {
        "$group": {
            "_id": {
                "dst_port": "$dst_port",
                "date": {
                    "$dateFromParts": {
                        "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                    }
                },
                "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
            },
            "count": {"$sum": 1}
        }
    },

    {
        "$group": {
            "_id": {
                "dst_port": "$_id.dst_port",
                "date": "$_id.date",
            },
            "hourly": {
                "$push": {
                    "$arrayToObject": {
                        "$concatArrays": [
                            [
                                {"k": {"$substr":["$_id.hour",0,-1]}, "v": "$count"}
                            ]
                        ]
                    }
                }
            },
            "counts": {"$sum": "$count"}
        }
    },

    {
        "$project":{
            "_id": 0,
            "port": "$_id.dst_port",
            "date": "$_id.date",
            "hourly": {"$mergeObjects": "$hourly"},
            "counts": 1
        }
    },

    {
        "$sort": {"date": 1, "counts": -1}
    },

    {
        "$out": "honeypot_events_port_timebased_metric"
    }
])
end_ts = time.time()
print (end_ts - start_ts)