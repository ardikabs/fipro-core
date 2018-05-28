
# Query untuk mendapatkan Data berdasarkan Metrics Country dan Port

from pymongo import MongoClient
import time
from datetime import datetime, timedelta
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()

# by_country_and_port = db.logs.aggregate([
#     {
#         "$match": {
#             "identifier": "uid-206189149201",
#             "geoip.country": {"$ne": None},
#             "dst_port": {"$ne": None}
#         }
#     },
#     {
#         "$group": {
#             "_id": {
#                 "country": "$geoip.country",
#                 "country_code": "$geoip.country_code",
#                 "dst_port": "$dst_port"
#             },
#             "count": {"$sum": 1}
#         }
#     },
#     {
#         "$group": {
#             "_id": {
#                 "country": "$_id.country",
#                 "country_code": "$_id.country_code"
#             },
#             "attacked_port": {
#                 "$push": {"port": "$_id.dst_port", "count": "$count"} 
#             },
#             "counts": {"$sum": "$count"}
#         }
#     },
#     {
#         "$sort": {"counts": -1, "attacked_port.count": -1}
#     },
#     {
#         "$project": {
#             "_id": 0,
#             "country": "$_id.country",
#             "country_code": "$_id.country_code",
#             "attacked_port": 1,
#             "counts": "$counts"
#         }
#     },
#     {
#         "$out": "honeypot_by_country_and_port_metric"
#     }
# ])

by_country_and_port_2nd = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-206189149201",
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
                    "$arrayToObject":{
                        "$concatArrays": [
                            [
                                {"k": {"$substr":["$_id.dst_port", 0, -1 ]}, "v":"$count"}
                            ]
                        ]
                    }
                }
            },
            "counts": {"$sum": "$count"}

        }
    },
    {
        "$sort": {"counts": -1, "attacked_port": -1}
    },
    {
        "$project": {
            "_id": 0,
            "country": "$_id.country",
            "country_code": "$_id.country_code",
            "attacked_port": {"$mergeObjects": "$attacked_port"},
            "counts":1
        }
    },
    { "$limit": 10},
    
    {
        "$out": "honeypot_top10_countries_and_port_metric"
    }
])
end_ts = time.time()
print (end_ts - start_ts)




# {
#     "$replaceRoot": {
#         "newRoot": {
#             "$arrayToObject":{
#                 "$concatArrays": [
#                     [
#                         {"k": "country", "v": "$_id.country"},
#                         {"k": "country_code", "v": "$_id.country_code"},
#                         {"k": "attacked_port", "v": {"k": {"$substr":["$_id.dst_port", 0, -1 ]}, "v":"$counts"}}
#                     ]
#                 ]
#             }
#         }
#     }
# },