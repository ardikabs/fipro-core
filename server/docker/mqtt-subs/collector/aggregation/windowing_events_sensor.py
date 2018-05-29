# Query untuk mendapatkan Data Metrics Event berdasarkan jenis Honeypot
# serta juga berdasarkan jenis Honeypot dan waktu per jam dan per hari

from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()


aggregate = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-206189149201",
            "timestamp": {"$gte": datetime.datetime.today() - datetime.timedelta(days=30) }
        }
    },

    {
        "$group": {
            "_id": {
                "honeypot": "$honeypot",
                "date": {
                    "$dateFromParts": {
                        "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                    }
                },
                "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
            },
            "uniqueValues":{"$addToSet": "$session"},
            "count": {"$sum": 1}
        }
    },

    {
        "$group": {
            "_id": {
                "honeypot": "$_id.honeypot",
                "date": "$_id.date"
            },
            "hourly":{
                "$push": {
                    "$arrayToObject": {
                        "$concatArrays": [
                            [
                                {"k": {"$substr":["$_id.hour",0,-1]}, 
                                    "v": {
                                        "$cond": {
                                            "if": {"$eq": ["$_id.honeypot", "cowrie"] },
                                            "then": {"$size": "$uniqueValues"},
                                            "else": "$count",
                                        }
                                    }
                                }
                            ]
                        ]
                    }
                }
            },
            "counts": {"$sum": {
                "$cond": {
                    "if": {"$eq": ["$_id.honeypot", "cowrie"] },
                    "then": {"$size": "$uniqueValues"},
                    "else": "$count",
                }
            }}
        }
    },


    {
        "$project":{
            "_id": 0,
            "honeypot": "$_id.honeypot",
            "date": "$_id.date",
            "hourly": {"$mergeObjects": "$hourly"},
            "counts": 1
        }
    },
    {
        "$sort": {"date": 1}
    },
    {
        "$out": "honeypot_events_sensor_timebased_metric"
    }
])
end_ts = time.time()
print (end_ts - start_ts)
