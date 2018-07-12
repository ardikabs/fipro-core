from pymongo import MongoClient
import time
import datetime
mongoconn = MongoClient('mongodb://mongo.wisperlabs.me:27020')
db = mongoconn.fipro
start_ts = time.time()

# aggregate_event = db.logs.aggregate([
#     {
#         "$match": {
#             "identifier": "uid-19216872129",
#             "geoip": {"$eq": None}
#         }
#     },

#     {
#         "$group": {
#             "_id": {
#                 "src_ip": "$src_ip",
#             },
#             "count": {"$sum": 1}
#         }
#     },

#     {
#         "$project":{
#             "_id": 0,
#             "src_ip": "$_id.src_ip",
#             "count": 1
#         }
#     },
#     {
#         "$sort": { "count": -1}
#     },
#     {
#         "$limit": 10
#     },
#     {
#         "$out": "honeypot_top10_unkown_source_ip_metric"
#     }
# ])

match = {
    "$match": {
        "identifier": "fb0963921f12",
        "dst_port": {"$ne":None}
        
    }
}
group = {
    "$group": {
        "_id": {
            "sensor": "$sensor",
            "agent_ip": "$agent_ip",
            "dst_port": "$dst_port"
        },
        "uniqueValues": {"$addToSet": "$session"},
        "count": {"$sum": 1}
    }
}

group2 = {
    "$group": {
        "_id": {
            "agent_ip": "$_id.agent_ip",
            "dst_port": "$_id.dst_port"
        },
        "count": {
            "$sum": {
                "$cond": {
                    "if": {"$eq": ["$_id.sensor", "cowrie"] },
                    "then": {"$size": "$uniqueValues"},
                    "else": "$count",
                }
            }
        }
        
    }
}
group3 = {
    "$group": {
        "_id": {
            "agent_ip": "$_id.agent_ip"
        },
        "infos": {
            "$push": {
                "dst_port": "$_id.dst_port",
                "count": "$count"
            }
        }
    }
}
sort = {"$sort": {"count": -1}}
limit = {"$limit": 10}
project = {
    "$project": {
        "_id":0,
        "agent": "$_id.agent_ip",
        "infos": {
            "$slice": ["$infos", 0, 10]
        }
    }
}
query_set = [match, group, group2, sort, group3, project]
result = db.logs.aggregate(query_set)
print (list(result))
end_ts = time.time()
print (end_ts - start_ts)