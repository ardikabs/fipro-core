
# Query untuk mendapatkan Data berdasarkan Metrics Country dan Port

from pymongo import MongoClient
import time
from datetime import datetime, timedelta
mongoconn = MongoClient('mongodb://192.168.1.100:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate = db.logs.aggregate([
    {
        "$match": {
            "identifier": "fb0963921f12",
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
            "count": {"$sum": 1}
        }
    },
    {
        "$group":{
            "_id": {
                "country": "$_id.country",
                "country_code": "$_id.country_code"
                
            },
            "attacked_port": {
                "$push": {
                    "dst_port": "$_id.dst_port", "counts": "$count" 
                }
            },
            "counts": {"$sum": "$count"}

        }
    },
    {
        "$sort": {"counts": -1, "attacked_port": -1}
    },
    {
        "$limit": 10
    },
    {
        "$project": {
            "_id": 0,
            "country": "$_id.country",
            "country_code": "$_id.country_code",
            "attacked_port": 1,
            "counts":1
        }
    },    
    {
        "$out": "honeypot_top10_countries_and_port_metric"
    }
])
end_ts = time.time()
print (end_ts - start_ts)