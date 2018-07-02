
import pymongo
import datetime
import pytz
from dateutil.relativedelta import relativedelta
import json
from bson import ObjectId, son
from app.utils import get_datetime, get_date, current_datetime


class MongoInterface():

    def __init__(self, mongodburl=None):

        # mongodburl = mongodburl or 'mongodb://localhost:27017'
        # self.client = pymongo.MongoClient(mongodburl,serverSelectionTimeoutMS=10, tz_aware=True)
        # self.client = pymongo.MongoClient(host="mongodb", port=27017, serverSelectionTimeoutMS=10, tz_aware=True)
        self.client = pymongo.MongoClient(host="mongo.wisperlabs.me", port=27020, serverSelectionTimeoutMS=10, tz_aware=True)
        try:
            self.client.server_info()
            self.conn = True
        except pymongo.errors.ServerSelectionTimeoutError as err:
            self.conn = False

    def check_conn(self):
        return self.conn

    @property
    def daily(self):
        return DailyCount(self.client)

    @property
    def ports(self):
        return PortCount(self.client)

    @property
    def sensor_event(self):
        return SensorEventCount(self.client)

    @property
    def logs(self):
        return Logs(self.client)

    def __repr__(self):
        return "<%s instance at %s>" % (self.__class__.__name__, id(self))
    
class ResourceMixin():
    
    db_name = "fipro"
    expected_filters = ('_id',)
    data_keys = tuple()

    def __init__(self, client=None, **kwargs):
        self.client = client

        for attr in self.__class__.expected_filters:
            setattr(self, attr, kwargs.get(attr))

    @property
    def collection(self):
        cls = self.__class__
        return self.client[cls.db_name][cls.collection_name]
    

    def new(self, **kwargs):
        return self.__class__.from_dict(kwargs, self.client)
    
    def get_one(self, **kwargs):
        query = self.__class__._clean_query(kwargs)
        return self.__class__.from_dict(
                self.collection.find_one(query), self.client
            )

    def get(self, options={}, **kwargs):

        if self.client is None:
            raise ValueError
        
        else:
            if '_id' in kwargs:
                kwargs['_id'] = ObjectId(kwargs['_id'])
                return self.__class__.from_dict(
                        self.collection.find_one(kwargs), self.client)

            query = self.__class__._clean_query(kwargs)
            queryset = self.collection.find(query)

            if options:
                skip, limit, order_by = self.__class__._clean_options(options)

                if skip:
                    queryset = queryset.skip(skip)
                if limit:
                    queryset = queryset.limit(limit)
                if order_by:
                    queryset = queryset.sort(order_by)


            return (self.__class__.from_dict(f, self.client) for f in queryset)

    def delete(self, **kwargs):
        query = dict()
        if kwargs:
            query = self.__class__._clean_query(kwargs)
        elif self._id:
            query = {'_id': self._id}
        else:
            return None
        
        return self.collection.remove(query)
      
    def count(self, **kwargs):
        query = self.__class__._clean_query(kwargs)
        return self.collection.find(query).count()

    def to_dict(self):
        todict = dict() 
        for key in self.data_keys:
            todict.update({key: getattr(self, key)})
        
        todict['_id'] = str(todict['_id'])
        return todict
        

    @classmethod
    def _clean_query(cls, dirty):
        clean = dict()
        for arg in cls.expected_filters:
            if dirty.get(arg):
                clean[arg] = dirty.get(arg)
        
        if 'today' in dirty:
            clean['timestamp'] = {
                '$gte': dirty['today'].replace(hour=0, minute=0, second=0),
                '$lte': dirty['today'].replace(hour=23, minute=59, second=59)
            }

        if 'hours_ago' in dirty:
            clean['timestamp'] = {
                '$gte': get_datetime( (datetime.datetime.now() - datetime.timedelta(hours=int(dirty['hours_ago']))).timestamp() )
            }
        
        if 'days_ago' in dirty:
            clean['date'] = {
                '$gte': get_date( (datetime.datetime.now() - datetime.timedelta(days=int(dirty['days_ago']) )).timestamp() )
            }

        if 'months_ago' in dirty:
            clean['date'] = {
                '$gte': get_date( (datetime.datetime.now() - relativedelta(months=int(dirty['months_ago']))) .timestamp() )
            }

        if 'years_ago' in dirty:
            clean['date'] = {
                '$gte': get_date( (datetime.datetime.now() - relativedelta(years=int(dirty['years_ago']))) .timestamp() )
            }

        return clean
    
    @classmethod
    def _clean_options(cls, opts):
        try:
            skip = int(opts.get('skip', 0))
        except (ValueError, TypeError):
            skip = 0

        limit = opts.get('limit', None)

        if limit:
            try:
                limit = int(limit)
            except (ValueError, TypeError):
                limit = 10
        
        order_by = opts.get('order_by', None)
        order_list = []
        if order_by:
            if isinstance(order_by, list):
                for order in order_by:
                    if order.startswith('-'):
                        direction = pymongo.DESCENDING
                    else:
                        direction = pymongo.ASCENDING
                    order = order.replace('-','')
                    order = (order, direction)
                    order_list.append(order)

            else:
                if order_by.startswith('-'):
                    direction = pymongo.DESCENDING
                else:
                    direction = pymongo.ASCENDING
                
                order_by = order_by.replace('-','')
                if order_by not in cls.expected_filters:
                    order_by = None
                else:
                    order_by = (order_by, direction)
                    order_list.append(order_by)


        return skip, limit, order_list

    @classmethod
    def from_dict(cls, dict_, client=None):

        if dict_ is None:
            return None
        
        doc = cls(client)
        attrs = dict_.keys()
        for at in attrs:
            doc.data_keys = doc.data_keys + (at,)
            setattr(doc, at, dict_.get(at))
        
        return doc

class DailyCount(ResourceMixin):

    collection_name = 'daily_count'
    expected_filters = ('date', 'identifier', 'type')

class PortCount(ResourceMixin):

    collection_name = 'port_count'
    expected_filters = ('date', 'identifier', 'type')

    def __init__(self, client=None):
        self.client = client

class SensorEventCount(ResourceMixin):
    
    collection_name = 'sensor_events_count'
    expected_filters = ('date', 'identifier', 'type')
    
    def get_one(self, **kwargs):
        if 'sensor' in kwargs:
            kwargs['type'] = "{}.events.count".format(kwargs['sensor'])

        query = self.__class__._clean_query(kwargs)
        return self.__class__.from_dict(
                self.collection.find_one(query), self.client
            )

    def get(self, options={}, **kwargs):
        if self.client is None:
            raise ValueError
        
        else:
            if 'sensor' in kwargs:
                kwargs['type'] = "{}.events.count".format(kwargs['sensor'])

            query = self.__class__._clean_query(kwargs)
            queryset = self.collection.find(query)           
            return (self.__class__.from_dict(f, self.client) for f in queryset)


class Logs(ResourceMixin):

    collection_name = 'logs'
    expected_filters = ('_id', 'identifier', 'sensor', 'agent_ip', 'timestamp', 'src_ip', 'dst_port')
 
    def top_asn(self, options={}, **kwargs):
       
        match_query = {
            "$match": 
            {
                "sensor": {"$ne": "cowrie"},
                "identifier": kwargs.get('identifier', None),
                "geoip.autonomous_system_number" : {"$ne": None}
            }
        }

        match2_query = {
            "$match":
            {
                "sensor": {"$eq": "cowrie"},
                "identifier": kwargs.get('identifier'),
                "geoip.autonomous_system_number" : {"$ne": None}
            }
        }
        
        group_query = {
            "$group":
            {
                "_id": {
                    "autonomous_system_number": "$geoip.autonomous_system_number",
                    "autonomous_system_organization": "$geoip.autonomous_system_organization"
                },
                "counts": {"$sum": 1}
            }
        }

        group2_query = {
            "$group":
            {
                "_id": {
                    "autonomous_system_number": "$_id.autonomous_system_number",
                    "autonomous_system_organization": "$_id.autonomous_system_organization"
                },
                "counts": {"$sum": 1}
            }
        }

        project_query = {
            "$project":{
                "_id": 0,
                "label": "$_id.autonomous_system_number",
                "autonomous_system_number": "$_id.autonomous_system_number",
                "autonomous_system_organization": "$_id.autonomous_system_organization",
                "counts": "$counts"
            }
        }
        sort = {"$sort": {"counts": -1}}
        unwind = {"$unwind": "$session"}
        limit = {"$limit": options.get('limit', 10)}

        query_set = [match_query, group_query, sort, limit, project_query]
        query1_set = [match2_query, group2_query, unwind, group2_query, project_query, sort, limit]

        nocowrie_dt = self.collection.aggregate(query_set)
        cowrie_dt = self.collection.aggregate(query1_set)
        
        return self._process_asn(nocowrie_dt, cowrie_dt)
    
    def _process_asn(self, nocowrie_dt, cowrie_dt):
        cowrie = [doc for doc in cowrie_dt]
        newdata = []

        for doc in nocowrie_dt:
            for dt in cowrie:
                if dt['autonomous_system_number'] == doc ['autonomous_system_number']:
                    doc['counts'] += dt['counts']
            newdata.append(doc)
        return newdata

    def top_countries_port(self, options={}, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "geoip.country": {"$ne": None},
                "dst_port": {"$ne": None}
            }
        }

        group_query = {
            "$group":{
                "_id": {
                    "country": "$geoip.country",
                    "country_code": "$geoip.country_code",
                    "dst_port": "$dst_port"
                },
                "count": {"$sum": 1}
            }
        }

        group1_query = {
            "$group":{
                "_id": {
                    "country": "$_id.country",
                    "country_code": "$_id.country_code"
                    
                },
                "attacked_port": {
                    "$push": {
                        "dst_port": "$_id.dst_port", 
                        "count": "$count" 
                    }
                },
                "counts": {"$sum": "$count"}

            }
        }

        project_query = {
            "$project": {
                "_id": 0,
                "label": "$_id.country",
                "country_code": "$_id.country_code",
                "attacked_port": 1,
                "counts":1
            } 
        }

        sort = {"$sort": {"counts": -1}}
        unwind = {"$unwind": "$attacked_port"}        
        limit = {'$limit': options.get('limit', 10)}

        query_set = [match_query, group_query, group1_query, sort, limit, project_query]
        res = self.collection.aggregate(query_set)
        return list(res)

    def top_countries(self, options={}, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "geoip.country": {"$ne": None}
            }
        }

        group_query = {
            "$group": {
                "_id": {
                    "country": "$geoip.country",
                    "country_code": "$geoip.country_code",
                },
                "counts": {"$sum": 1}
            }  
        }

        project_query = {
            "$project": {
                "_id": 0,
                "label": "$_id.country",
                "country_code": "$_id.country_code",
                "counts": "$counts"
            }
        }

        sort = {"$sort": {"counts": -1}}
        limit = {'$limit': options.get('limit', 10)}

        query_set = [match_query, group_query, project_query, sort, limit]
        res = self.collection.aggregate(query_set)
        return list(res)

    def top_sourceip(self, options={}, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "geoip": {"$ne": None}
            }
        }

        group_query = {
            "$group": {
                "_id": {
                    "src_ip": "$src_ip",
                    "country": "$geoip.country",
                    "country_code": "$geoip.country_code"
                },
                "counts": {"$sum": 1}
            }
        }

        project_query = {
            "$project":{
                "_id": 0,
                "label": "$_id.src_ip",
                "country": "$_id.country",
                "country_code": "$_id.country_code",
                "counts": 1
            }
        }
        sort = {"$sort": {"counts": -1}}
        limit = {'$limit': options.get('limit', 10)}

        query_set = [match_query, group_query, project_query, sort, limit]
        res = self.collection.aggregate(query_set)
        return list(res)
    
    def top_unknown_sourceip(self, options={}, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "geoip": {"$eq": None}
            }
        }

        group_query = {
            "$group": {
                "_id": {
                    "src_ip": "$src_ip",
                },
                "counts": {"$sum": 1}
            }
        }

        project_query = {
            "$project":{
                "_id": 0,
                "label": "$_id.src_ip",
                "counts": 1
            }
        }
        sort = {"$sort": {"counts": -1}}
        limit = {'$limit': options.get('limit', 10)}

        query_set = [match_query, group_query, project_query, sort, limit]
        res = self.collection.aggregate(query_set)
        return list(res)

    def top_sourceip_port(self, options={}, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "geoip.country": {"$ne": None},
                "dst_port": {"$ne": None}
            }
        }

        group_query = {
            "$group": {
                "_id": {
                    "src_ip": "$src_ip",
                    "country": "$geoip.country",
                    "country_code": "$geoip.country_code",
                    "dst_port": "$dst_port"

                },
                "count": {"$sum": 1}
            }
        }

        group1_query = {
            "$group":{
                "_id": {
                    "src_ip": "$_id.src_ip",
                    "country": "$_id.country",
                    "country_code": "$_id.country_code"
                    
                },
                "attacked_port": { 
                    "$push": {
                        "dst_port": "$_id.dst_port", 
                        "count": "$count" 
                    }
                },
                "counts": {"$sum": "$count"}
            }
        }

        project_query = {
            "$project":{
                "_id": 0,
                "label": "$_id.src_ip",
                "label_1": "$_id.country",
                "country_code": "$_id.country_code",
                "attacked_port": 1,
                "counts":1
            }
        }
        sort = {"$sort": {"counts": -1}}
        unwind = {"$unwind": "$attacked_port"}

        query_set = [match_query, group_query, group1_query, sort, unwind, project_query]
        res = self.collection.aggregate(query_set)
        return list(res)

    def event_statistics(self, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "timestamp": self._timestamp(kwargs)
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
                    "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                },
                "uniqueValues":{"$addToSet": "$session"},
                "count": {"$sum": 1}
            }
        }

        group1_query = {
            "$group": {
                "_id": {
                    "identifier":"$_id.identifier",
                    "sensor": "$_id.sensor",
                    "date": "$_id.date"
                },
                "hourly":{
                    "$push": {
                        "hour": "$_id.hour",
                        "count": {
                            "$cond": {
                                "if": {"$eq": ["$_id.sensor", "cowrie"] },
                                "then": {"$size": "$uniqueValues"},
                                "else": "$count",
                            }
                        }
                    }
                },
            }
        }

        group2_query = {
            "$group": {
                "_id": {
                    "identifier": "$_id.identifier",
                    "date": "$_id.date",
                    "hour": "$hourly.hour"
                },
                "count": {"$sum": "$hourly.count"}
            }
        }

        group3_query = {
            "$group": {
                "_id": {
                    "identifier": "$_id.identifier",
                    "date": "$_id.date"
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
                "label": "$_id.identifier",
                "date": "$_id.date",
                "hourly": {"$mergeObjects": "$hourly"},
                "counts": 1
            }
        }

        unwind = {"$unwind": "$hourly"}
        sort = {"$sort": {"date": 1}}
        
        query_set = [match_query, group_query, group1_query, unwind, group2_query, group3_query, project_query, sort]
        res = self.collection.aggregate(query_set)
        return list(res)

    def sensor_event_statistics(self, **kwargs):

        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "timestamp": self._timestamp(kwargs)
            }
        }
        
        group_query = {
            "$group": {
                "_id": {
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
                    "sensor": "$_id.sensor",
                    "date": "$_id.date"
                },
                "hourly":{
                    "$push": {
                        "$arrayToObject": {
                            "$concatArrays": [
                                [
                                    {"k": {"$substr":["$_id.hour",0,-1]}, 
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
                "label": "$_id.sensor",
                "hourly": {"$mergeObjects": "$hourly"},
                "counts": 1
            }
        }
        sort = {"$sort": {"date": 1}}
        query_set = [match_query, group_query, group1_query, project_query, sort]
        res = self.collection.aggregate(query_set)
        
        return list(res)
        
    def agents_event_statistics(self, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "timestamp": self._timestamp(kwargs)
            }
        }

        group_query = {
            "$group": {
                "_id": {
                    "sensor": "$sensor",
                    "agent_ip": "$agent_ip",
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
                    "sensor": "$_id.sensor",
                    "agent_ip": "$_id.agent_ip",
                    "date": "$_id.date"

                },
                "hourly":{
                    "$push": {
                        "hour": "$_id.hour",
                        "count": {
                            "$cond": {
                                "if": {"$eq": ["$_id.sensor", "cowrie"] },
                                "then": {"$size": "$uniqueValues"},
                                "else": "$count",
                            }
                        }
                    }
                },
            }
        }

        group2_query = {
            "$group": {
                "_id": {
                    "date": "$_id.date",
                    "agent_ip": "$_id.agent_ip",
                    "hour": "$hourly.hour"

                },
                "count": {"$sum": "$hourly.count"}
            }
        }
        
        group3_query = {
            "$group": {
                "_id": {
                    "date": "$_id.date",
                    "agent_ip": "$_id.agent_ip"

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
                "date": "$_id.date",
                "label": "$_id.agent_ip",
                "hourly": {"$mergeObjects": "$hourly"},
                "counts": 1
            }
        }
        unwind = {"$unwind": "$hourly"}
        sort = {"$sort": {"date": 1}}
        limit = {"$limit": kwargs.get('limit',10)}

        query_set = [match_query, group_query, group1_query, unwind, group2_query, group3_query, project_query, sort]
        if kwargs.get('limit'):
            query_set.append(limit)
        res = self.collection.aggregate(query_set)
        return list(res)
    
    def countries_event_statistics(self, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "timestamp": self._timestamp(kwargs),
                "geoip.country": {"$ne": None}
            }
        }

        group_query = {
            "$group": {
                "_id": {
                    "country": "$geoip.country",
                    "country_code": "$geoip.country_code",
                    "date": {
                        "$dateFromParts": {
                            "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                            "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                            "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                        }
                    },                
                    "hour": {"$hour": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                },
                "count": {"$sum": 1}
            }
        }

        group1_query = {
            "$group": {
                "_id": {
                    "country": "$_id.country",
                    "country_code": "$_id.country_code",
                    "date": "$_id.date"
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
            "$project": {
                "_id": 0,
                "label": "$_id.country",
                "country_code": "$_id.country_code",
                "date": "$_id.date",
                "hourly": {"$mergeObjects": "$hourly"},
                "counts": 1
            }
        }

        limit = {"$limit": kwargs.get('limit',10)}
        sort = {"$sort": {"date": 1, "counts": -1}}

        query_set = [match_query, group_query, group1_query, project_query, sort]
        if kwargs.get('limit'):
            query_set.append(limit)
            
        res = self.collection.aggregate(query_set)
        return list(res)

    def ports_event_statistics(self, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "timestamp": self._timestamp(kwargs),
                "dst_port": {"$ne": None}
            }
        }

        group_query = {
            "$group": {
                "_id": {
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
                "date": "$_id.date",
                "hourly": {"$mergeObjects": "$hourly"},
                "counts": 1
            }
        }
        
        limit = {"$limit": kwargs.get('limit',10)}
        sort = {"$sort": {"date": 1, "counts": -1}}
        query_set = [match_query, group_query, group1_query, project_query, sort]
        if kwargs.get('limit'):
            query_set.append(limit)

        res = self.collection.aggregate(query_set)
        return list(res)
    
    def events_count(self, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier')
            }
        }

        group_query = {
            "$group": {
                "_id": {
                    "sensor": "$sensor"
                },
                "uniqueValues":{"$addToSet": "$session"},
                "counts": {"$sum": 1}
            }
        }

        project_query = {
            "$project":{   
                "_id":0,
                "label": "$_id.sensor",
                "counts": { 
                    "$cond": { 
                        "if": {"$eq": ["$_id.sensor", "cowrie"] }, 
                        "then": {"$size": "$uniqueValues"},
                        "else": "$counts" 
                    }
                },
            }
        }
        

        if kwargs.get("today"):
            today = {
                "timestamp": {
                    "$gte": kwargs.get("today").replace(hour=0, minute=0, second=0),
                    "$lte": kwargs.get("today").replace(hour=23, minute=59, second=59)
                }
            }
            match_query.get('$match').update(today)
            
        
        query_set = [match_query, group_query, project_query]
        res = self.collection.aggregate(query_set)
        return list(res)

    def ports_events_count(self, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "dst_port": {"$ne": None}
            }
        }

        group_query = {
            "$group": {
                "_id": {
                    "dst_port": "$dst_port",
                },
                "counts": {"$sum": 1}
            }            
        }
        
        project_query = {
            "$project":{
                "_id": 0,
                "label": "$_id.dst_port",
                "counts": 1
            }
        }
        
        limit = {"$limit": kwargs.get('limit',10)}
        sort = {"$sort": {"date": 1, "counts": -1}}
        query_set = [match_query, group_query, project_query, sort]
        if kwargs.get('limit'):
            query_set.append(limit)

        res = self.collection.aggregate(query_set)
        return list(res)   

    def username_list(self, **kwargs):
        match_query = {
            "$match":{
                "identifier": kwargs.get('identifier'),
                "$and": [ {"username": {"$ne": None} }, {"username": {"$ne": ""}} ]
            }
        }

        group_query = {
            "$group":{
                "_id": "$username",
                "counts": {"$sum": 1}  
            }
        }

        project_query = {
            "$project": {
                "_id": 0,
                "label": "$_id.username",
                "counts": 1
            }
        }

        sort = {"$sort": {"counts": -1}}
        query_set = [match_query, group_query, project_query, sort]
        res = self.collection.aggregate(query_set)
        return list(res)

    def password_list(self, **kwargs):
        match_query = {
            "$match":{
                "identifier": kwargs.get('identifier'),
                "$and": [ {"password": {"$ne": None} }, {"password": {"$ne": ""}} ]
            }
        }

        group_query = {
            "$group":{
                "_id": "$password",
                "counts": {"$sum": 1}  
            }
        }

        
        project_query = {
            "$project": {
                "_id": 0,
                "label": "$_id.password",
                "counts": 1
            }
        }

        sort = {"$sort": {"counts": -1}}
        query_set = [match_query, group_query, project_query, sort]
        res = self.collection.aggregate(query_set)
        return list(res)

    def ports_histogram(self, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "dst_port": {"$ne": None}
            }
        }
        
        group_query = {
            "$group": {
                "_id": {
                    "dst_port": "$dst_port",
                    "date": {
                        "$dateFromParts": {
                            "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                            "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                            "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                        }
                    },
                },
                "count": {"$sum": 1}
            } 
        }

        group1_query = {
            "$group": {
                "_id": {
                    "dst_port": "$_id.dst_port",
                },
                "infos": {
                    "$push": {
                        "date": "$_id.date",
                        "count": "$count"
                    }
                },
                "counts": {"$sum": "$count"}
            } 
        }
    
        project_query = {
            "$project": {
                "_id": 0,
                "label": "$_id.dst_port",
                "infos": 1,
                "count":1,
                "counts": 1
            }
        }

        unwind = {"$unwind": "$infos"}
        sort = {"$sort": {"counts": -1}}
        sort_date = {"$sort": {"infos.date": 1}}
        limit = {"$limit": kwargs.get('limit',10)}

        query_set = [match_query, group_query, group1_query, sort, limit, unwind, sort_date, project_query]
            
        res = self.collection.aggregate(query_set)
        return list(res)

    def countries_histogram(self, **kwargs):
        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
                "geoip.country": {"$ne": None}
            }
        }
        
        group_query = {
            "$group": {
                "_id": {
                    "country": "$geoip.country",
                    "country_code": "$geoip.country_code",
                    "date": {
                        "$dateFromParts": {
                            "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                            "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                            "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                        }
                    }                
                },
                "count": {"$sum": 1}
            }
        }

        group1_query = {
            "$group": {
                "_id": {
                    "country": "$_id.country",
                    "country_code": "$_id.country_code",
                },
                "infos": {
                    "$push":{
                        "date": "$_id.date",
                        "count": "$count"
                    } 
                },
                "counts": {"$sum": "$count"}
            }
        }
    
        project_query = {
            "$project": {
                "_id": 0,
                "label": "$_id.country",
                "country_code": "$_id.country_code",
                "infos": 1,
                "count":1,
                "counts": 1
            }
        }

        unwind = {"$unwind": "$infos"}
        sort = {"$sort": {"counts": -1}}
        sort_date = {"$sort": {"infos.date": 1}}
        limit = {"$limit": kwargs.get('limit',10)}

        query_set = [match_query, group_query, group1_query, sort, limit, unwind, sort_date, project_query]
            
        res = self.collection.aggregate(query_set)
        return list(res)

    def events_histogram(self, **kwargs):

        match_query = {
            "$match": {
                "identifier": kwargs.get('identifier'),
            }
        }
        
        group_query = {
            "$group": {
                "_id": {
                    "sensor": "$sensor",
                    "date": {
                        "$dateFromParts": {
                            "year": {"$year": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                            "month": {"$month": {"date": "$timestamp", "timezone": "Asia/Jakarta"}},
                            "day": {"$dayOfMonth": {"date": "$timestamp", "timezone": "Asia/Jakarta"}}
                        }
                    },
                },
                "uniqueValues":{"$addToSet": "$session"},
                "count": {"$sum": 1}
            }
        }

        group1_query = {
            "$group": {
                "_id": {
                    "sensor": "$_id.sensor",
                },
                "infos":{
                    "$push": {
                        "date": "$_id.date",
                        "count": {
                            "$cond": {
                                "if": {"$eq": ["$_id.sensor", "cowrie"] },
                                "then": {"$size": "$uniqueValues"},
                                "else": "$count",
                            }
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
                "label": "$_id.sensor",
                "infos": 1,
                "counts": 1
            }
        }
        unwind = {"$unwind": "$infos"}
        sort = {"$sort": {"counts": -1}}
        sort_date = {"$sort": {"infos.date": 1}}
        limit = {"$limit": kwargs.get('limit',10)}   

        query_set = [match_query, group_query, group1_query, sort, limit, unwind, sort_date, project_query]
        res = self.collection.aggregate(query_set)
        
        return list(res)
        
    def _timestamp(self, opt):
        
        if "years_ago" in opt:
            return {"$gte": current_datetime() - datetime.timedelta(days= int(opt.get('years_ago', 1))*365 ) }

        elif "months_ago" in opt:
            return {"$gte": current_datetime() - datetime.timedelta(days= int(opt.get('months_ago', 1))*30 ) }
        
        elif "days_ago" in opt:
            return {"$gte": current_datetime() - datetime.timedelta(days= int(opt.get('days_ago', 7)) ) }

        elif "date" in opt:
            time = opt.get('date')
            gte = time.replace(hour= 17, minute= 0, second= 0) - datetime.timedelta(days=1)
            lte = time.replace(hour= 16, minute= 59, second= 59)
            return {"$gte": gte, "$lte": lte }
        
    
    def recent_attacks(self, options={}, **kwargs):
        newdata = []
        data = self.get(options, **kwargs)
        for dt in data:
            dt.data_keys = dt.data_keys + ('counts',)
            setattr(dt, 'counts', dt.count(src_ip=dt.src_ip))
            newdata.append(dt.to_dict())
        
        return newdata
