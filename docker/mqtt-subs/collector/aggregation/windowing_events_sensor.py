# Query untuk mendapatkan Data Metrics Event berdasarkan jenis sensor
# serta juga berdasarkan jenis sensor dan waktu per jam dan per hari

from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongo.wisperlabs.me:27020')
db = mongoconn.fipro
start_ts = time.time()


aggregate = db.new_logs.aggregate([
    {
        "$match": {
            "identifier": "fb0963921f12",
            "timestamp": {"$gte": datetime.datetime.today() - datetime.timedelta(hours=24) }
        }
    },

    {
        "$group": {
            "_id": {
                "sensor": "$sensor",
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
                "sensor": "$_id.sensor",
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
                                            "if": {"$eq": ["$_id.sensor", "cowrie"] },
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
                    "if": {"$eq": ["$_id.sensor", "cowrie"] },
                    "then": {"$size": "$uniqueValues"},
                    "else": "$count",
                }
            }}
        }
    },


    {
        "$project":{
            "_id": 0,
            "date": "$_id.date",
            "sensor": "$_id.sensor",
            "hourly": {"$mergeObjects": "$hourly"},
            "counts": 1
        }
    },
    {
        "$sort": {"date": 1}
    }
])
end_ts = time.time()
print (list(aggregate))
print (end_ts - start_ts)

