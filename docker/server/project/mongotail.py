import pymongo
import time
import datetime
import pytz
client = pymongo.MongoClient(host="mongo.wisperlabs.me", port=27020, serverSelectionTimeoutMS=10, tz_aware=True)

col = client.fipro.sensor.log
last_ts = col.find().sort('timestamp',-1).limit(-1).next()['timestamp']
tail_opts = { "cursor_type": pymongo.CursorType.TAILABLE_AWAIT}
while True:
    query = {'timestamp': {'$gte': datetime.datetime.fromtimestamp(last_ts.timestamp(), tz=pytz.utc)}}
    cursor = col.find(query, **tail_opts)
    try:
        while cursor.alive:
            try:
                doc = cursor.next()
                print (doc)
            except StopIteration:
                time.sleep(1)
    finally:
        cursor.close()
