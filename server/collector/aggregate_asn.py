

from pymongo import MongoClient
import time
from datetime import datetime, timedelta
mongoconn = MongoClient('mongodb://192.168.1.100:27017/')
db = mongoconn.fipro

start = time.time()
# hours_top_10_asn_aggregate = db.logs.aggregate([
#     {
#         "$match":{
#             "timestamp":{
#                 "$gte": datetime.now() - timedelta(hours=10)
#             }
#         }
#     },
#     {
#         "$group":
#         {
#             "_id":{
#                 "honeypot": "$honeypot",
#                 "autonomous_system_number": "$location.autonomous_system_number"
#             },
#             "uniqueIP":{"$addToSet": "$src_ip"},
#             "counts":{"$sum": 1}
#         }
#     },
#     {
#         "$project":{
#             "_id": 0,
#             "honeypot": "$_id.honeypot"
#         }
#     },
#     {}
# ])

match_without_time = {"$match": 
        {
            "honeypot": {"$ne": "cowrie"},
            "geoip.autonomous_system_number" : {"$ne": None}
        }
    }

match_with_time = {"$match": 
        {
            "honeypot": {"$ne": "cowrie"},
            "geoip.autonomous_system_number" : {"$ne": None},
            "timestamp":{"$gte": datetime.now() - timedelta(hours=10)}
        }
    }

group_top10_asn = {"$group":
        {
            "_id": {
                "autonomous_system_number": "$geoip.autonomous_system_number",
                "autonomous_system_organization": "$geoip.autonomous_system_organization"
            },
            "counts": {"$sum": 1}
        }
    }

sort_desc_counts = {"$sort": {"counts": -1}}

projects_top10_asn = {"$project":
        {
            "_id": 0,
            "autonomous_system_number": "$_id.autonomous_system_number",
            "autonomous_system_organization": "$_id.autonomous_system_organization",
            "counts": "$counts"
        }
    }

match_with_time_cowrie = {"$match": 
    {
        "honeypot": {"$eq": "cowrie"},
        "geoip.autonomous_system_number" : {"$ne": None},
        "timestamp":{"$gte": datetime.now() - timedelta(hours=10)}
    }
}

match_without_time_cowrie = {"$match": 
    {
        "honeypot": {"$eq": "cowrie"},
        "geoip.autonomous_system_number" : {"$ne": None}
    }
}

group_asn_cowrie = {"$group":
    {
        "_id":{
            "autonomous_system_number": "$geoip.autonomous_system_number",
            "autonomous_system_organization": "$geoip.autonomous_system_organization"
        },
        "session": { "$addToSet": "$session"}
    }
}
unwind_cowrie = {"$unwind": "$session"}


start_ts = time.time()
top_10_asn_aggregate_cowrie = db.logs.aggregate([
    match_without_time_cowrie,
    group_asn_cowrie,
    unwind_cowrie,
    group_top10_asn,
    sort_desc_counts,
    projects_top10_asn
])


top_10_asn_aggregate = db.logs.aggregate([
    match_without_time,
    group_top10_asn,
    sort_desc_counts,
    projects_top10_asn
])

docs_cowrie = [doc for doc in top_10_asn_aggregate_cowrie]
databaru = []


for doc in top_10_asn_aggregate:
    for doc_cowrie in docs_cowrie:
        if doc_cowrie['autonomous_system_number'] == doc['autonomous_system_number']:
            print("ASN: {}".format(doc_cowrie['autonomous_system_number']))
            print("Before count: {}".format(doc_cowrie['counts']))

            doc['counts'] += doc_cowrie['counts']

            print("ASN: {}".format(doc['autonomous_system_number']))
            print("After count: {}".format(doc['counts']))

                
    databaru.append(doc)

db.honeypot_top_asn_metric.insert_many(databaru)
end_ts = time.time()

print (end_ts - start_ts)









