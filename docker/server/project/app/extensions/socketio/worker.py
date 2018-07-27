import json
import pymongo
import datetime
import pytz
import time
from bson import json_util

from app.commons.MongoInterface import MongoInterface as MoI
from app import mongo as mongo_client

class RecentAttacksWorker:

    switch = False
    num_of_work = 0

    def __init__(self, socketio):
        self.socketio = socketio
        self.switch = True
    
    def run(self, *args, **kwargs):
        identifier = kwargs.get('identifier')

        col = mongo_client.db.sensor.log
        last_ts = col.find({'identifier': identifier}).sort('timestamp',-1).limit(-1).next()['timestamp']
        query = {'identifier': identifier ,'timestamp': {'$gte': datetime.datetime.fromtimestamp(last_ts.timestamp(), tz=pytz.utc)}}
        tail_opts = { "cursor_type": pymongo.CursorType.TAILABLE_AWAIT}
        
        cursor = col.find(query, **tail_opts)
        print ("Status: Cursor Open")
        while self.switch:
            try:    
                while cursor.alive:
                    if self.switch is False:
                        cursor.close()

                    try:
                        doc = cursor.next()
                        if doc.get('sensor') == 'cowrie':
                            check = col.find({'session': doc.get('session')}).count()
                            if check == 1:
                                data = list(col.aggregate([
                                    {'$match': {'identifier': identifier, 'sensor': 'cowrie', 'src_ip': doc.get('src_ip')}},
                                    {'$group': {'_id': {'src_ip': '$src_ip'}, 'uniqueValues': {'$addToSet': '$session'}}},
                                    {'$project': {'_id':0, 'src_ip': '$_id.src_ip', 'count': {'$size': '$uniqueValues'}}}
                                ]))
                                doc['count'] = data[0].get('count', 0)
                                self.socketio.emit('recent_attacks', json.dumps(doc, default=json_util.default), namespace="/socket.io")
                        
                        else:
                            doc['count'] = col.find({'identifier': identifier, 'src_ip': doc['src_ip']}).count()
                            self.socketio.emit('recent_attacks', json.dumps(doc, default=json_util.default), namespace="/socket.io")
                        
                    except StopIteration:
                        time.sleep(1)
            finally:
                cursor.close()
                print ("Status: Cursor Closed")

            self.socketio.sleep(10)
        
    def stop(self):
        self.switch = False