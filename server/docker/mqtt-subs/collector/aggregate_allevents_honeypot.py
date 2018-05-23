from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://206.189.149.230:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-206189149201"
        }
    },
    {
        "$group": {
            "_id": {
                "type": {
                            "$switch":
                            {
                                "branches": [
                                    {
                                        "case": {"$eq": ["$honeypot","dionaea"]},
                                        "then": "dionaea.event.counts"
                                    },
                                    {
                                        "case": {"$eq": ["$honeypot","cowrie"]},
                                        "then": "cowrie.event.counts"
                                    },
                                    {
                                        "case": {"$eq": ["$honeypot","glastopf"]},
                                        "then": "glastopf.event.counts"
                                    }
                                ],
                                "default": "no events"
                            }
                        },
                "identifier": "$identifier"
            },
            "uniqueValues":{"$addToSet": "$session"},
            "counts": {"$sum": 1}
        },
    },
    {
        "$project":{   
            "_id":0,
            "type": "$_id.type",
            "identifier":"$_id.identifier",
            "event_counts": 
                { 
                    "$cond": { 
                        "if": {"$eq": ["$_id.type", "cowrie.event.counts"] }, 
                        "then": {"$size": "$uniqueValues"},
                        "else": "$counts" 
                    }
                },
        }
    },
    {
        "$out": "honeypot_allevents_metric"
    }
])

end_ts = time.time()

print (end_ts - start_ts)