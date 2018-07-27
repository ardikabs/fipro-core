
import datetime
import pytz
from celery_worker import celery
from celery.schedules import crontab
from app import mongo

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    
    sender.add_periodic_task(60.0, aggregate_sensor_event.s("AGGREGATION SENSOR EVENT"), name='Aggregation Sensor Event per hour')
    sender.add_periodic_task(60.0, aggregate_port_event.s("AGGREGATION PORT EVENT"), name='Aggregation Dest. Port Event per hour')
    sender.add_periodic_task(60.0, aggregate_countries_event.s("AGGREGATION COUNTRIES EVENT"), name='Aggregation Country Event per hour')

@celery.task
def aggregate_sensor_event(arg):
    print (arg)
    coll = mongo.db.aggregate.sensorevents

    date_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    check = coll.find_one()
    
    if check:
        print ("Check {}".format(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
        lte = date_now.replace(hour=16, minute=59, second=59)
        gte = date_now.replace(hour=17, minute=0, second=0) - datetime.timedelta(days=1)
        time = {"$lte": lte, "$gte": gte}
        query_set = get_query_sensor(time)
        query_set = query_set[:-1]
        result = list(mongo.db.sensor.log.aggregate(query_set, allowDiskUse=True))

        for res in result:
            identifier = res.get('identifier')
            label = res.get('label')
            date = res.get('date')
            newdict = dict()
            newdict['counts'] = res.get('counts')
            hourly = res.get('hourly')
            for k in hourly:
                key = "hourly.{}".format(k)
                newdict[key] = hourly.get(k)
            

            coll.update_many({'date': date, 'identifier': identifier, 'label': label},
                {'$set': newdict},
                upsert=True
            )
    
    else:
        print ("No Check Data")
        lte = date_now.replace(hour=16, minute=59, second=59)
        time = {"$lte": lte}
        query_set = get_query_sensor(time)
        mongo.db.sensor.log.aggregate(query_set, allowDiskUse=True)

@celery.task
def aggregate_port_event(arg):
    print (arg)
    coll = mongo.db.aggregate.portevents

    date_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    check = coll.find_one()

    if check:
        print ("Check {}".format(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
        lte = date_now.replace(hour=16, minute=59, second=59)
        gte = date_now.replace(hour=17, minute=0, second=0) - datetime.timedelta(days=1)
        time = {"$lte": lte, "$gte": gte}
        query_set = get_query_port(time)
        query_set = query_set[:-1]
        result = list(mongo.db.sensor.log.aggregate(query_set, allowDiskUse=True))

        for res in result:
            identifier = res.get('identifier')
            label = res.get('label')
            date = res.get('date')

            newdict = dict()
            newdict['counts'] = res.get('counts')
            hourly = res.get('hourly')
            for k in hourly:
                key = "hourly.{}".format(k)
                newdict[key] = hourly.get(k)
            

            coll.update_many({'date': date, 'identifier': identifier, 'label': label},
                {'$set': newdict},
                upsert=True
            )
    
    else:
        print ("No Check Data")
        lte = date_now.replace(hour=16, minute=59, second=59)
        time = {"$lte": lte}
        query_set = get_query_port(time)
        mongo.db.sensor.log.aggregate(query_set, allowDiskUse=True)

@celery.task
def aggregate_countries_event(arg):
    print (arg)
    coll = mongo.db.aggregate.countriesevents

    date_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    check = coll.find_one()

    if check:
        print ("Check {}".format(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
        lte = date_now.replace(hour=16, minute=59, second=59)
        gte = date_now.replace(hour=17, minute=0, second=0) - datetime.timedelta(days=1)
        time = {"$lte": lte, "$gte": gte}
        query_set = get_query_country(time)
        query_set = query_set[:-1]
        result = list(mongo.db.sensor.log.aggregate(query_set, allowDiskUse=True))        

        for res in result:
            
            identifier = res.get('identifier')
            label = res.get('label')
            date = res.get('date')

            newdict = dict()
            newdict['counts'] = res.get('counts')
            hourly = res.get('hourly')
            for k in hourly:
                key = "hourly.{}".format(k)
                newdict[key] = hourly.get(k)
            
            coll.update_many(
                {'date': date, 'identifier': identifier, 'label': label},
                {'$set': newdict},
                upsert=True
            )
    else:
        print ("No Check Data")
        lte = date_now.replace(hour=16, minute=59, second=59)
        time = {"$lte": lte}
        query_set = get_query_country(time)
        mongo.db.sensor.log.aggregate(query_set, allowDiskUse=True)




def get_query_country(time):
    match_query = {
        "$match": {
            "timestamp": time,
            "geoip.country": {"$ne": None}
        }
    }

    group_query = {
        "$group": {
            "_id": {
                "identifier": "$identifier",
                "country": "$geoip.country",
                "country_code": "$geoip.country_code",
                "sensor":"$sensor",
                "date": {
                    "$dateFromParts": {
                        "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                    }
                },                
                "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
            },
            "uniqueValues":{"$addToSet": "$session"},
            "count": {"$sum": 1}
        }
    }

    group1_query = {
        "$group": {
            "_id": {
                "identifier": "$_id.identifier",
                "country": "$_id.country",
                "country_code": "$_id.country_code",
                "date": "$_id.date"
            },
            "hourly": {
                "$push": {
                    "$arrayToObject": {
                        "$concatArrays": [
                            [
                                {
                                    "k": {"$substr":["$_id.hour",0,-1]}, 
                                    "v": {
                                        "$cond": {
                                            "if": {"$eq": ["$_id.sensor", "cowrie"] },
                                            "then": {"$size": "$uniqueValues"},
                                            "else": "$count",
                                        }
                                    }
                                }
                            ]
                        ]
                    }
                }
            },
            "counts": {"$sum": {
                "$cond": {
                    "if": {"$eq": ["$_id.sensor", "cowrie"] },
                    "then": {"$size": "$uniqueValues"},
                    "else": "$count",
                }
            }}
        }
    }

    project_query = {
        "$project": {
            "_id": 0,
            "label": "$_id.country",
            "identifier": "$_id.identifier",
            "date": "$_id.date",
            "country_code": "$_id.country_code",
            "hourly": {"$mergeObjects": "$hourly"},
            "counts": 1
        }
    }

    sort = {"$sort": {"date": -1, "counts": -1}}
    out = {"$out": "aggregate.countriesevents"}

    query_set = [match_query, group_query, group1_query, project_query, sort, out]
    return query_set

def get_query_port(time):
    match_query = {
        "$match": {
            "timestamp": time,
            "dst_port": {"$ne": None}
        }
    }

    group_query = {
        "$group": {
            "_id": {
                "identifier": "$identifier",
                "dst_port": "$dst_port",
                "date": {
                    "$dateFromParts": {
                        "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                    }
                },
                "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
            },
            "count": {"$sum": 1}
        }            
    }

    group1_query = {
        "$group": {
            "_id": {
                "identifier": "$_id.identifier",
                "dst_port": "$_id.dst_port",
                "date": "$_id.date",
            },
            "hourly": {
                "$push": {
                    "$arrayToObject": {
                        "$concatArrays": [
                            [
                                {"k": {"$substr":["$_id.hour",0,-1]}, "v": "$count"}
                            ]
                        ]
                    }
                }
            },
            "counts": {"$sum": "$count"}
        }        
    }
    
    project_query = {
        "$project":{
            "_id": 0,
            "label": "$_id.dst_port",
            "identifier": "$_id.identifier",
            "date": "$_id.date",
            "hourly": {"$mergeObjects": "$hourly"},
            "counts": 1
        }
    }
    
    sort = {"$sort": {"date": -1, "counts": -1}}
    out = {"$out": "aggregate.portevents"}

    query_set = [match_query, group_query, group1_query, project_query, sort, out]
    return query_set

def get_query_sensor(time):
    match_query = {
        "$match": {
            "timestamp": time
        }
    }
    
    group_query = {
        "$group": {
            "_id": {
                "identifier": "$identifier",
                "sensor": "$sensor",
                "date": {
                    "$dateFromParts": {
                        "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                        "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                    }
                },
                "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
            },
            "uniqueValues":{"$addToSet": "$session"},
            "count": {"$sum": 1}
        }
    }

    group1_query = {
        "$group": {
            "_id": {
                "identifier": "$_id.identifier",
                "sensor": "$_id.sensor",
                "date": "$_id.date"
            },
            "hourly":{
                "$push": {
                    "$arrayToObject": {
                        "$concatArrays": [
                            [
                                {
                                    "k": {"$substr":["$_id.hour",0,-1]}, 
                                    "v": {
                                        "$cond": {
                                            "if": {"$eq": ["$_id.sensor", "cowrie"] },
                                            "then": {"$size": "$uniqueValues"},
                                            "else": "$count",
                                        }
                                    }
                                }
                            ]
                        ]
                    }
                }
            },
            "counts": {"$sum": {
                "$cond": {
                    "if": {"$eq": ["$_id.sensor", "cowrie"] },
                    "then": {"$size": "$uniqueValues"},
                    "else": "$count",
                }
            }}
        }
    }

    project_query = {
        "$project":{
            "_id": 0,
            "date": "$_id.date",
            "identifier": "$_id.identifier",
            "label": "$_id.sensor",
            "hourly": {"$mergeObjects": "$hourly"},
            "counts": 1
        }
    }
    sort = {"$sort": {"date": -1}}
    out = {"$out": "aggregate.sensorevents"}
    query_set = [match_query, group_query, group1_query, project_query, sort, out]
    return query_set