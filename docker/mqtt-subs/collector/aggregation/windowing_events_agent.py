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

    # Grouped based on Honeypot | Date | Hour
    {
        "$group": {
            "_id": {
                "honeypot": "$honeypot",
                "dst_ip": "$dst_ip",
                "date": {
                    "$dateFromParts": {
                        "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                    }
                },
                "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
            },
            "uniqueValues":{"$addToSet": "$session"},
            "count": {"$sum": 1}
        }
    },

    # Grouped based on Honeypot | Date
    {
        "$group": {
            "_id": {
                "honeypot": "$_id.honeypot",
                "dst_ip": "$_id.dst_ip",
                "date": "$_id.date"

            },
            "hourly":{
                "$push": {
                    "hour": "$_id.hour",
                    "count": {
                        "$cond": {
                            "if": {"$eq": ["$_id.honeypot", "cowrie"] },
                            "then": {"$size": "$uniqueValues"},
                            "else": "$count",
                        }
                    }
                }
            },
        }
    },

    # Separate Array of Hour of each Data
    {
        "$unwind": "$hourly"
    },

    # Grouped based on Date and Hour
    {
        "$group": {
            "_id": {
                "date": "$_id.date",
                "dst_ip": "$_id.dst_ip",
                "hour": "$hourly.hour"

            },
            "count": {"$sum": "$hourly.count"}
        }
    },

    # Grouped based on Date
    {
        "$group": {
            "_id": {
                "date": "$_id.date",
                "dst_ip": "$_id.dst_ip"

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
            "date": "$_id.date",
            "agent": "$_id.dst_ip",
            "hourly": {"$mergeObjects": "$hourly"},
            "counts": 1
        }
    },
    {
        "$sort": {"date": 1}
    },
    {
        "$out": "honeypot_events_agent_timebased_metric"
    }
])

end_ts = time.time()
print (end_ts - start_ts)

