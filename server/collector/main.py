
from pymongo import MongoClient
from models import AttackDailyStats, AttackedPortStats, CredentialsCounts, SensorEventCounts
from utils import get_date, get_hour
import paho.mqtt.client as mqtt
import os
import sys
import json
import time
import datetime
import constant

''' Environment Variable Configuration '''
if os.path.exists('.env'):
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]
   

########################################################################
##################### MONGODB CONFIGURATION ############################
########################################################################
mongoconn = MongoClient(os.getenv('MONGODB_URL'))
db = mongoconn.fipro
coll_raw    = db.raw_log
coll_log    = db.logs
coll_ads    = db.attack_daily_stats
coll_aps    = db.attacked_port_stats
coll_sec    = db.sensor_event_counts
coll_cc     = db.credentials_counts
########################################################################

########################################################################
# [START] Honeypot Resolver
def cowrie_resolver(data):
    exist_session = [c for c in coll_log.find({"honeypot":"cowrie"}).distinct("session")]
    if data["session"] not in exist_session: # Check Existing Session dengan Session Data yang masuk
        attack_daily_proc(data) 
        attacked_port_proc(data)
        sensor_event_proc(data)
    
    if "username" in data:        
         credential_counts_proc(data)
              
def dionaea_resolver(data):
    if "username" in data:        
        credential_counts_proc(data)
    
    attack_daily_proc(data)
    attacked_port_proc(data)
    sensor_event_proc(data)

def glastopf_resolver(data):
    attack_daily_proc(data)
    attacked_port_proc(data)
    sensor_event_proc(data)

# [END] Honeypot Resolver
########################################################################

########################################################################
# [START] Processing
def attack_daily_proc(data):
    date= get_date(data["timestamp"])
    hour= get_hour(data["timestamp"])
    coll_dt = coll_ads.find({"date": get_date(data["timestamp"])}).count() # Variable untuk mengetahui jumlah data pada collection ADS sesuai dengan tanggal
    if coll_dt == 0:  # Ketika jumlah data 0 maka membuat dokumen baru
        newdata = AttackDailyStats(data)
        coll_ads.insert(newdata.to_mongo())
    else:
        mongodata = coll_ads.find({"date": date},{"hourly."+ hour:{'$exists':True}}).count() # Digunakan untuk cek pada dokumen dan mengetahui telah terdapat tanggal sesuai dengan data baru atau tidak 
        existdata = AttackDailyStats(data)
        if mongodata == 0:
            coll_ads.update({"date": get_date(data["timestamp"])}, 
                            existdata.to_set(), 
                            True, False)
        else:
            coll_ads.update({"date": get_date(data["timestamp"])}, 
                            existdata.to_inc())  

def attacked_port_proc(data):
    date= get_date(data["timestamp"])
    coll_dt = coll_aps.find({"date":get_date(data["timestamp"])}).count()
    if coll_dt == 0:
        newdata = AttackedPortStats(data)
        coll_aps.insert(newdata.to_mongo())
    else:
        mongodata = coll_aps.find({"date": date}, {"ports."+ str(data["dst_port"]):{"$exists":True}}).count()
        existdata = AttackedPortStats(data)
        if mongodata == 0:
            coll_aps.update({"date": get_date(data["timestamp"])}, 
                            existdata.to_set(), 
                            True, False)
        else:
            coll_aps.update({"date": get_date(data["timestamp"])},
                            existdata.to_inc())
        
def credential_counts_proc(data):
    coll_dt = coll_cc.find().count()
    if coll_dt == 0:
        newdata = CredentialsCounts(None,data)
        coll_cc.insert(newdata.to_mongo())
    else:
        mongodata = coll_cc.find_one()
        existdata = CredentialsCounts(mongodata,data)
        if existdata.checkNone():
            pass
        else:
            coll_cc.update({"type":"credentials.counts"}, 
                        existdata.to_update(), 
                        True, False)     

def sensor_event_proc(data):
    date= get_date(data["timestamp"])
    identifier= data["identifier"]

    dt = coll_sec.find({"date":date,"identifier":identifier}).count()

    if dt == 0:
        newdata = SensorEventCounts(data)
        coll_sec.insert(newdata.to_mongo())
    else:
        existdata = SensorEventCounts(data)
        coll_sec.update({"date":date,"identifier":identifier}, 
                        existdata.to_update())

def geoip_attacks_proc(data):
    pass
# [END] Processing
########################################################################

########################################################################
###################### MAIN WORKER PROGRAM #############################
########################################################################
# [START] MQTT Component
def on_connect(client, userdata, flags, rc):
    print ("... %s is Listening ..." % client._client_id)
    client.subscribe("honeypot/cowrie")
    client.subscribe("honeypot/dionaea")
    client.subscribe("honeypot/glastopf")

def on_message(client,userdata,message):
    # insertion data to database
    if message.topic == "honeypot/cowrie":
        cowrie_resolver(json.loads(message.payload))
    elif message.topic == "honeypot/dionaea":
        dionaea_resolver(json.loads(message.payload))
    elif message.topic == "honeypot/glastopf":
        glastopf_resolver(json.loads(message.payload))

    coll_log.insert(json.loads(message.payload))

def main():
    client = mqtt.Client(client_id="COLLECTOR.HoneypotSubscriber", clean_session=False)
    client.username_pw_set(os.getenv('USERNAME_MQTT') or 'mycollector',password=os.getenv('PASSWD_MQTT') or 'rustygear125')
    client.on_connect = on_connect
    client.on_message = on_message
    # client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pem', tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(host=os.getenv('MQTT_URL'), port=1883)
    client.loop_forever()

# [END] MQTT Component
if __name__ == "__main__":
    try:
        print ("### START SESSION of Python MQTT Client ###")
        main()
    except KeyboardInterrupt:
        print ("### END SESSION of Python MQTT Client ###")
    sys.exit(0)