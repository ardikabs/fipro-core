from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate_uid_only = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-206189149201"
        }
    },
    {
        "$group": {
            "_id": {
                "honeypot": "$honeypot"
            },
            "uniqueValues":{"$addToSet": "$session"},
            "counts": {"$sum": 1}
        },
    },
    {
        "$project":{   
            "_id":0,
            "honeypot": "$_id.honeypot",
            "identifier":"$_id.identifier",
            "counts": { 
                "$cond": { 
                    "if": {"$eq": ["$_id.honeypot", "cowrie"] }, 
                    "then": {"$size": "$uniqueValues"},
                    "else": "$counts" 
                }
            },
        }
    },
    {
        "$out": "honeypot_alltime_events_metric"
    }
])

end_ts = time.time()

print (end_ts - start_ts)