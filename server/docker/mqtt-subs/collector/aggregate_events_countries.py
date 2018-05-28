
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
            "identifier": "uid-206189149201",
            "timestamp": {"$gte": datetime.datetime.today() - datetime.timedelta(days=2) }
        }
    },
    {
        "$group": {
            "_id": {
                "country": "$geoip.country",
                "country_code": "$geoip.country_code",
                "date": {"$dateToString": {"format": "%Y-%m-%d %H:00", "date": "$timestamp", "timezone": "Asia/Jakarta"}}
            },
            "counts": {"$sum": 1}
        }
    },
    {
        "$sort": {"date": -1}
    },
    {
        "$project": {
            "_id": 0,
            "country": "$_id.country",
            "country_code": "$_id.country_code",
            "date": "$_id.date",
            "counts": "$counts"
        }
    },
    {
        "$out": "honeypot_events_countries_timebased_metric"
    }
])

end_ts = time.time()
print (end_ts - start_ts)





