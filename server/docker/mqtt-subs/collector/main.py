
from pymongo import MongoClient
from models import AttackDailyStats, AttackedPortStats, CredentialCount, SensorEventsCount, GeoIP
from utils import get_date, get_hour, get_year
import paho.mqtt.client as mqtt
import geoip2.database
import geoip2.errors
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
coll_raw     = db.raw_log
coll_log     = db.logs
coll_metrics = db.metrics


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

    type= "attack.daily.stats"
    dt = coll_metrics.find({"type": type, "date": get_date(data["timestamp"])}).count() # Variable untuk mengetahui jumlah data pada collection ADS sesuai dengan tanggal
    if dt == 0:  # Ketika jumlah data 0 maka membuat dokumen baru
        newdata = AttackDailyStats(data)
        coll_metrics.insert(newdata.to_mongo())
    else:
        mongodata = coll_metrics.find({"type": type,"date": date},{"hourly."+ hour:{'$exists':True}}).count() # Digunakan untuk cek pada dokumen dan mengetahui telah terdapat tanggal sesuai dengan data baru atau tidak 
        existdata = AttackDailyStats(data)
        if mongodata == 0:
            coll_metrics.update({"type": type, "date": get_date(data["timestamp"])}, 
                            existdata.to_set(), 
                            True, False)
        else:
            coll_metrics.update({"type": type, "date": get_date(data["timestamp"])}, 
                            existdata.to_inc())  

def attacked_port_proc(data):
    date= get_date(data["timestamp"])
    type= "attacked.port.stats"
    dt = coll_metrics.find({"type": type, "date": get_date(data["timestamp"])}).count()
    if dt == 0:
        newdata = AttackedPortStats(data)
        coll_metrics.insert(newdata.to_mongo())
    else:
        mongodata = coll_metrics.find({"type": type, "date": date}, {"ports."+ str(data["dst_port"]):{"$exists":True}}).count()
        existdata = AttackedPortStats(data)
        if mongodata == 0:
            coll_metrics.update({"type": type, "date": get_date(data["timestamp"])}, 
                            existdata.to_set(), 
                            True, False)
        else:
            coll_metrics.update({"type": type, "date": get_date(data["timestamp"])},
                            existdata.to_inc())
        
def credential_counts_proc(data):
    type = "credential.count"
    dt = coll_metrics.find({"type": type, "date": get_year(data['timestamp'])}).count()
    if dt == 0:
        newdata = CredentialCount(None,data)
        coll_metrics.insert(newdata.to_mongo())
    else:
        mongodata = coll_metrics.find_one({"type": type, "date":get_year(data['timestamp'])})
        existdata = CredentialCount(mongodata,data)
        if existdata.checkNone():
            pass
        else:
            coll_metrics.update({"type":type, "date":get_year(data['timestamp'])}, 
                        existdata.to_update(), 
                        True, False)     

def sensor_event_proc(data):
    date= get_date(data["timestamp"])
    identifier= data["identifier"]
    type= "{0}.events.count".format(data["honeypot"])

    dt = coll_metrics.find({"type": type,"date": date,"identifier": identifier}).count()

    if dt == 0:
        newdata = SensorEventsCount(data)
        coll_metrics.insert(newdata.to_mongo())
    else:
        existdata = SensorEventsCount(data)
        coll_metrics.update({"type": type, "date": date,"identifier": identifier}, 
                        existdata.to_update())

       

def data_to_hmaps(data):
    pass


def data_to_mongo(data):
    data['timestamp'] = datetime.datetime.fromtimestamp(data['timestamp'])
    coll_log.insert(data)


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
    client.subscribe("honeypot")

def on_message(client,userdata,message):
    # insertion data to database
    data = json.loads(message.payload.decode("utf-8"))

    geoip = GeoIP(data["src_ip"])
    if geoip.not_found() == True:
        data['geoip'] = None
    else:
        data['geoip'] = geoip.to_dict()

    if message.topic == "honeypot/cowrie":
        cowrie_resolver(data)
    elif message.topic == "honeypot/dionaea":
        dionaea_resolver(data)
    elif message.topic == "honeypot/glastopf":
        glastopf_resolver(data)

    data_to_hmaps(data)
    data_to_mongo(data)

def main():
    client = mqtt.Client(client_id="COLLECTOR.HoneypotSubscriber", clean_session=False)
    client.username_pw_set(os.getenv('USERNAME_MQTT') or 'mycollector',password=os.getenv('PASSWD_MQTT') or 'rustygear125')
    client.on_connect = on_connect
    client.on_message = on_message
    # client.tls_set('/etc/ssl/certs/DST_Root_CA_X3.pem', tls_version=ssl.PROTOCOL_TLSv1_2)
    client.connect(host="mqtt-broker", port=1883)
    client.loop_forever()

# [END] MQTT Component
if __name__ == "__main__":
    try:
        print ("### START SESSION of Python MQTT Client ###")
        main()
    except KeyboardInterrupt:
        print ("### END SESSION of Python MQTT Client ###")
    sys.exit(0)