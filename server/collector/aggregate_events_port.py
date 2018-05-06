from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://192.168.1.100:27017/')
db = mongoconn.fipro
start_ts = time.time()

aggregate_event = db.logs.aggregate([
    {
        "$match": {
            "identifier": "uid-1921681100",
            "dst_port": {"$ne": None},
            "timestamp": {"$gte": datetime.datetime.today() - datetime.timedelta(weeks=80) }
        }
    },

    {
        "$group": {
            "_id": {
                "dst_port": "$dst_port",
                "date": {"$dateToString": {"format": "%Y%m%d", "date": "$timestamp", "timezone": "Asia/Jakarta"}},
                "hourly": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
            },
            "counts": {"$sum": 1}
        }
    },

    {
        "$project":{
            "_id": 0,
            "port": "$_id.dst_port",
            "date": "$_id.date",
            "hourly": "$_id.hourly",
            "counts": 1
        }
    },

    {
        "$out": "honeypot_events_dest_port_metric"
    }
])
end_ts = time.time()
print (end_ts - start_ts)