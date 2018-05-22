# Query untuk mendapatkan Data Metrics Event berdasarkan jenis Honeypot
# serta juga berdasarkan jenis Honeypot dan waktu per jam dan per hari

from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()

# aggregate = db.logs.aggregate([
#     {
#         "$match": {
#             "identifier": "uid-1921681100"
#         }
#     },
#     {
#         "$group": {
#             "_id": {
#                 "type": {
#                             "$switch":
#                             {
#                                 "branches": [
#                                     {
#                                         "case": {"$eq": ["$honeypot","dionaea"]},
#                                         "then": "dionaea.event.counts"
#                                     },
#                                     {
#                                         "case": {"$eq": ["$honeypot","cowrie"]},
#                                         "then": "cowrie.event.counts"
#                                     },
#                                     {
#                                         "case": {"$eq": ["$honeypot","glastopf"]},
#                                         "then": "glastopf.event.counts"
#                                     }
#                                 ],
#                                 "default": "no events"
#                             }
#                         },
#                 "timestamp": {"$dateToString": {"format": "%Y%m%d", "date": "$timestamp", "timezone": "Asia/Jakarta"}},
#                 "identifier": "$identifier"
#             },
#             "uniqueValues":{"$addToSet": "$session"},
#             "counts": {"$sum": 1}
#         },
#     },
#     {
#         "$project":{   
#             "_id":0,
#             "type": "$_id.type",
#             "date": "$_id.timestamp",
#             "identifier":"$_id.identifier",
#             "event_counts": 
#                 { 
#                     "$cond": { 
#                         "if": {"$eq": ["$_id.type", "cowrie.event.counts"] }, 
#                         "then": {"$size": "$uniqueValues"},
#                         "else": "$counts" 
#                     }
#                 },
#         }
#     },
#     {
#         "$out": "honeypot_events_metric"
#     }
# ])

aggregate_event = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-206189149201",
            "timestamp": {"$gte": datetime.datetime.today() - datetime.timedelta(weeks=52) }
        }
    },

    {
        "$group": {
            "_id": {
                "honeypot": "$honeypot",
                "date": {"$dateToString": {"format": "%Y%m%d", "date": "$timestamp", "timezone": "Asia/Jakarta"}},
                "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
            },
            "count": {"$sum": 1}
        }
    },

    {
        "$project":{
            "_id": 0,
            "honeypot": "$_id.honeypot",
            "date": "$_id.date",
            "hour": "$_id.hour",
            "count": 1
        }
    },

    {
        "$group": {
            "_id": {
                "honeypot": "$honeypot",
                "date": "$date"
            },
            "hourly": {"$addToSet": {"hour":"$hour", "count": "$count"}},
            "counts": {"$sum": "$count"}
        }
    },

    {
        "$project":{
            "_id": 0,
            "honeypot": "$_id.honeypot",
            "date": "$_id.date",
            "hourly": 1,
            "count": 1
        }
    },

    {
        "$out": "honeypot_events_metric"
    }
])
end_ts = time.time()
print (end_ts - start_ts)