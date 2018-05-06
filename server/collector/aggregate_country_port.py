

from pymongo import MongoClient
import time
from datetime import datetime, timedelta
mongoconn = MongoClient('mongodb://192.168.1.100:27017/')
db = mongoconn.fipro
start_ts = time.time()

by_country_and_port = db.logs.aggregate([
    {
        "$match": {
            "geoip.country": {"$ne": None},
            "dst_port": {"$ne": None}
        }
    },
    {
        "$group": {
            "_id": {
                "country": "$geoip.country",
                "country_code": "$geoip.country_code",
                "dst_port": "$dst_port"
            },
            "counts": {"$sum": 1}
        }
    },
    {
        "$sort": {"counts": -1}
    },
    {
        "$project": {
            "_id": 0,
            "country": "$_id.country",
            "country_code": "$_id.country_code",
            "port": "$_id.dst_port",
            "counts": "$counts"
        }
    },
    {
        "$out": "honeypot_by_country_and_port_metric"
    }
])

end_ts = time.time()
print (end_ts - start_ts)





