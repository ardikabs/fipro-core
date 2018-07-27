
import pymongo
import datetime
import pytz
from dateutil.relativedelta import relativedelta
import json
from bson import ObjectId, son
from app.utils import get_datetime, get_date, current_datetime
from app import mongo

class IMongo:

    def __init__(self):
        self.client = mongo

    def check_connection(self):
        conn = True
        try:
            self.client.cx.server_info()
            conn = True
        except pymongo.errors.ServerSelectionTimeoutError as err:
            conn = False
        
        return conn

    @property
    def sensor_logs(self):
        return SensorLogs(self.client)

class ResourceMixin:
    db_name = 'fipro'
    expected_filters = ('id',)
    custom_keys = tuple()

    def __init__(self, client=None, **kwargs):
        self.client = client

        for attr in self.__class__.expected_filters:
            setattr(self, attr, kwargs.get(attr))
    

    @property
    def collection(self):
        cls = self.__class__
        return self.client.db[cls.collection_name]
    
    def new(self, **kwargs):
        return self.__class__.from_dict(kwargs, self.client)
    
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
                    self.collection.find_one(kwargs), self.client
                )
            
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
    

    def to_dict(self):
        newdict = dict()
        
        if self.custom_keys:
            for key in self.custom_keys:
                newdict[key] = getattr(self, key)

                if isinstance(newdict[key], datetime.datetime):
                    newdict[key] = newdict[key].isoformat()

        else:
            for attr in self.expected_filters:
                newdict[attr] = getattr(self, attr)

                if isinstance(newdict[key], datetime.datetime):
                    newdict[key] = newdict[key].isoformat()
        
        if '_id' in newdict:
            newdict['_id'] = str(newdict['_id'])
        return newdict

    @classmethod
    def _clean_query(cls, dirty):
        clean = dict()

        for arg in cls.expected_filters:
            if dirty.get(arg):
                clean[arg] = dict.get(arg)
        
        if 'days_ago' in dirty:
            clean['timestamp'] = {
                '$gte': datetime.datetime.utcnow() - datetime.timedelta(days=int(dirty['days_ago']))
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
                    direction = -1
                else:
                    direction = 1

                if order_by not in cls.expected_filters:
                    order_by = None
                else:
                    order = (order_by, direction)
                    order_list.append(order)

        return skip, limit, order_by


    @classmethod
    def from_dict(cls, dict_, client=None):
        if dict_ is None:
            return None
        
        doc = cls(client)
        attrs = dict_.keys()
        for attr in attrs:
            doc.custom_keys = doc.custom_keys + (attr,)
            setattr(doc, attr, dict_.get(attr))
        
        return doc


class SensorLogs(ResourceMixin):

    collection_name = 'sensor.logs'
    expected_filters = ('_id', 'identifier', 'sensor', 'agent_ip', 'src_ip', 'dst_port','timestamp')

