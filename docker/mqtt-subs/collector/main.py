
from pymongo import MongoClient
from models import (
    AttackDailyStats, 
    AttackedPortStats, 
    CredentialCount, 
    SensorEventsCount, 
    GeoIP
)
import paho.mqtt.client as mqtt
import os
import sys
import json
import logging
import utils

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

''' Environment Variable Configuration '''
if os.path.exists('.env'):
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]
   

########################################################################
##################### MONGODB CONFIGURATION ############################
########################################################################
mongoconn = MongoClient(host="mongodb",port=27017)
db = mongoconn.fipro
coll_log     = db.logs
coll_metrics = db.metrics

coll_daily   = db.daily_count
coll_port    = db.port_count
coll_hpot    = db.sensor_events_count
coll_cred    = db.credential_count


########################################################################

########################################################################
# [START] Honeypot Resolver
def cowrie_resolver(data):
    exist_session = [c for c in coll_log.find({"sensor":"cowrie"}).distinct("session")]
    if data["session"] not in exist_session: # Check Existing Session dengan Session Data yang masuk
        daily_counter(data) 
        port_counter(data)
        event_counter(data)
    
def dionaea_resolver(data):
    
    daily_counter(data)
    port_counter(data)
    event_counter(data)

def glastopf_resolver(data):
    daily_counter(data)
    port_counter(data)
    event_counter(data)

# [END] Honeypot Resolver
########################################################################

########################################################################
# [START] Processing
def daily_counter(data):
    type = "attack.daily.stats"
    date = utils.get_date(data['timestamp'])
    hour = utils.get_hour(data["timestamp"])
    identifier = data['identifier'] 

    # Variable untuk mengetahui jumlah data pada collection ADS sesuai dengan tanggal
    dt = coll_daily.find({"type": type, "date": date, "identifier": identifier }).count() 
    if dt == 0:  # Ketika jumlah data 0 maka membuat dokumen baru
        newdata = AttackDailyStats(data)
        coll_daily.insert(newdata.to_mongo())
    
    else:
        # Digunakan untuk cek pada dokumen dan mengetahui telah terdapat tanggal sesuai dengan data baru atau tidak
        mongodata = coll_daily.find({"type": type,"date": date, "identifier": identifier }, {"hourly."+ hour: {'$exists':True}}).count()  

        existdata = AttackDailyStats(data)
        if mongodata == 0:
            coll_daily.update({"type": type, "date": date}, existdata.to_set(), True, False)
        else:
            coll_daily.update({"type": type, "date": date}, existdata.to_inc())  

def port_counter(data):
    if "dst_port" not in data:
        return

    type = "attacked.port.stats"
    date = utils.get_date(data['timestamp'])
    identifier = data['identifier']

    dt = coll_port.find({"type": type, "date": date, "identifier": identifier }).count()
    
    if dt == 0:
        newdata = AttackedPortStats(data)
        coll_port.insert(newdata.to_mongo())

    else:
        mongodata = coll_port.find({"type": type, "date": date, "identifier": identifier },{"ports."+ str(data["dst_port"]):{"$exists":True}}).count()
                                    
        existdata = AttackedPortStats(data)
        if mongodata == 0:
            coll_port.update({"type": type, "date": date,"identifier": identifier}, existdata.to_set(), True, False)
        else:
            coll_port.update({"type": type, "date": date,"identifier": identifier }, existdata.to_inc())

def event_counter(data):
    type= "{0}.events.count".format(data["sensor"])
    date= utils.get_date(data['timestamp'])
    identifier= data["identifier"]

    dt = coll_hpot.find({"type": type,"date": date,"identifier": identifier }).count()

    if dt == 0:
        newdata = SensorEventsCount(data)
        coll_hpot.insert(newdata.to_mongo())

    else:
        existdata = SensorEventsCount(data)
        coll_hpot.update({"type": type, "date": date,"identifier": identifier }, existdata.to_update())

# [NOTUSED] CREDENTIAL
def credential_counter(data):
    type = "credential.count"
    date = utils.get_year(data['timestamp'])
    identifier = data['identifier']

    dt = coll_cred.find({"type": type, "date": date, "identifier": identifier }).count()
    
    if dt == 0:
        newdata = CredentialCount(None,data)
        coll_cred.insert(newdata.to_mongo())

    else:
        mongodata = coll_metrics.find_one({"type": type, "date": date, "identifier": identifier})

        existdata = CredentialCount(mongodata,data)
        if existdata.checkNone():
            pass
        else:
            coll_cred.update({"type":type, "date": date, "identifier": identifier}, existdata.to_update(), True, False)     
# [NOTUSED] CREDENTIAL


       
# [ONGOING] HONEYPOT MAPS
def data_to_hmaps(data):
    pass
# [ONGOING] HONEYPOT MAPS

def data_to_mongo(data):
    data['timestamp'] = utils.get_datetime(data['timestamp'])
    coll_log.insert(data)


# [END] Processing
########################################################################

########################################################################
###################### MAIN WORKER PROGRAM #############################
########################################################################
# [START] MQTT Component
def on_connect(client, userdata, flags, rc):
    print ("... %s is Listening ..." % client._client_id)
    client.subscribe("honeypot/cowrie",qos=2)
    client.subscribe("honeypot/dionaea",qos=2)
    client.subscribe("honeypot/glastopf",qos=2)

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
def runner():
    try:
        print ("### START SESSION of Python MQTT Client ###")
        main()
    except KeyboardInterrupt:
        print ("### END SESSION of Python MQTT Client ###")
        sys.exit(0)
    except Exception:
        import traceback
        import datetime
        print ("\n\nDate: ".format(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))

        logging.warning("Raised Error")
        print (">>> Error raised <<<\n\n")
        traceback.print_exc(file=sys.stdout)
        print ("\n\n################################\n\n")
        runner()

if __name__ == "__main__":
    runner()