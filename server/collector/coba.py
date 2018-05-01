

from pymongo import MongoClient
import time
mongoconn = MongoClient('mongodb://192.168.1.100:27017/')
db = mongoconn.fipro

start = time.time()
optimasi_sensor_event_count = db.raw_log.aggregate([
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
        "$out": "coba-cok"
    }
])


end = time.time()
now = end - start
minute = now / 60
seconds = now % 60
print (minute)
print (seconds)











# import geoip2.database

# reader = geoip2.database.Reader('./db/GeoLite2-City.mmdb')
# reader_asn = geoip2.database.Reader('./db/GeoLite2-ASN.mmdb')
# reader_country = geoip2.database.Reader('./db/GeoLite2-Country.mmdb')

# response = reader.city('85.25.43.84')
# response_asn = reader_asn.asn('103.24.56.245')
# response_country = reader_country.country('103.24.56.245')

# # print (response.city.names['en'])

# # print (response.continent.names['en'])
# # print (response.country.names['en'])

# # print (response.location.longitude)
# # print (response.location.latitude)
# # print (response.location.time_zone)

# # print (response.registered_country)
# print (response.subdivisions.most_specific.names['en'])
# print (response.subdivisions.most_specific.iso_code)
# print (response.postal.code)
