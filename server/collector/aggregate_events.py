from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://192.168.1.100:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate = db.logs.aggregate([
    {
        "$group": 
        {
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
                "timestamp": {"$dateToString": {"format": "%Y%m%d", "date": "$timestamp", "timezone": "Asia/Jakarta"}},
                "identifier": "$identifier"
            },
            "uniqueValues":{"$addToSet": "$session"},
            "counts": {"$sum": 1}
        },
    },
    {
        "$project":
        {   
            "_id":0,
            "type": "$_id.type",
            "date": "$_id.timestamp",
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
        "$out": "honeypot_events_metric"
    }
])

aggregate_event = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-1921681100",
            "timestamp": {"$gte": datetime.datetime.today() - datetime.timedelta(weeks=52) }
        }
    },

    {
        "$group": {
            "_id": {
                "honeypot": "$honeypot",
                "date": {"$dateToString": {"format": "%Y%m%d", "date": "$timestamp", "timezone": "Asia/Jakarta"}},
                "hourly": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
            },
            "counts": {"$sum": 1}
        }
    },

    {
        "$project":{
            "_id": 0,
            "honeypot": "$_id.honeypot",
            "date": "$_id.date",
            "hourly": "$_id.hourly",
            "counts": 1
        }
    },
    {
        "$out": "honeypot_events_metric"
    }
])
end_ts = time.time()
print (end_ts - start_ts)