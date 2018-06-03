
from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate = db.logs.aggregate([
    {
        "$match": {
            "geoip.country": {"$ne": None},
            "identifier": "5c3669d44b6a",
            "timestamp": {"$gte": datetime.datetime.today() - datetime.timedelta(days=5) }
        }
    },
    {
        "$group": {
            "_id": {
                "country": "$geoip.country",
                "country_code": "$geoip.country_code",
                "date": {
                    "$dateFromParts": {
                        "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                    }
                },                
                "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
            },
            "count": {"$sum": 1}
        }
    },
    {
        "$group": {
            "_id": {
                "country": "$_id.country",
                "country_code": "$_id.country_code",
                "date": "$_id.date"
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
        "$project": {
            "_id": 0,
            "country": "$_id.country",
            "country_code": "$_id.country_code",
            "date": "$_id.date",
            "hourly": {"$mergeObjects": "$hourly"},
            "counts": 1
        }
    },
    {
        "$sort": {"date": 1, "counts": -1}
    },
    {
        "$out": "honeypot_events_countries_timebased_metric"
    }
])

end_ts = time.time()
print (end_ts - start_ts)





