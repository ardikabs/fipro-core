
# Query untuk mendapatkan Top 10 Countries

from pymongo import MongoClient
import time
from datetime import datetime, timedelta
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate = db.logs.aggregate([
    {
        "$match": {
            "geoip.country": {"$ne": None},
            "identifier": "5c3669d44b6a"
        }
    },
    {
        "$group": {
            "_id": {
                "country": "$geoip.country",
                "country_code": "$geoip.country_code",
            },
            "counts": {"$sum": 1}
        }
    },
    {
        "$sort": {"counts": -1}
    },
    {
        "$limit": 10
    },
    {
        "$project": {
            "_id": 0,
            "country": "$_id.country",
            "country_code": "$_id.country_code",
            "counts": "$counts"
        }
    },
    {
        "$out": "honeypot_top10_countries_metric"
    }
])

end_ts = time.time()
print (end_ts - start_ts)





