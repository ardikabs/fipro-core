
import datetime
from utils import get_date, get_hour

class AttackDailyStats:
    def __init__(self,data):
        self._type = "attack.daily.stats"
        self._date = get_date(data["timestamp"])
        self._hours = get_hour(data["timestamp"])
        self._hourly = {self._hours: 1}
    
    def to_set(self):
        return {"$set": {"hourly."+self._hours: 1}}
    def to_inc(self):
        return {"$inc": {"hourly."+self._hours: 1}}
    def to_mongo(self):
        return dict(type = self._type, 
                    date = self._date, 
                    hourly = self._hourly)

class AttackedPortStats:
    def __init__(self,data):
        self._type = "attacked.port.stats"
        self._date = datetime.datetime.fromtimestamp(float(data["timestamp"])).strftime("%Y%m%d")
        self._port = str(data["dst_port"])
        self._ports = {str(data["dst_port"]): 1}
    
    def to_set(self):
        return {"$set": {"ports."+self._port: 1}}
    def to_inc(self):
        return {"$inc": {"ports."+self._port: 1}}
    def to_mongo(self):
        return dict(type = self._type, 
                    date = self._date, 
                    ports = self._ports)

class CredentialsCounts:
    def __init__(self,mongodata,data):
        self.mongodata = mongodata
        self.data = data
        self._type = "credentials.counts"
        self._username_list = {} if mongodata is None or "username_list" not in mongodata else mongodata["username_list"]   
        self._password_list = {} if mongodata is None or "password_list" not in mongodata else mongodata["password_list"]
        self._newdata = {}
        self._incdata = {}
        self._setdata = {}
        
        if mongodata is None:
            self._newdata = self._init_data()
        else:
            self._compute()

    def _init_data(self):
        initdata = dict(type = self._type)
        self._username_list[str(self.data["username"])] = 1
        self._password_list[str(self.data["password"])] = 1

        if self.data["username"] is not "":
            initdata["username_list"] = self._username_list
        if self.data["password"] is not "":
            initdata["password_list"] = self._password_list

        return initdata

    def _compute(self):
        if self.data["username"] in self._username_list:
            self._incdata["username_list."+ self.data["username"]] = 1
        else:
            if self.data["username"] is not "":
                self._setdata["username_list."+ self.data["username"]] = 1
        
        if self.data["password"] in self._password_list:
            self._incdata["password_list."+ self.data["password"]] = 1
        else:
            if self.data["password"] is not "":
                self._incdata["password_list."+ self.data["password"]] = 1       

    def to_update(self):
        if self._setdata and self._incdata:
            return {"$set": self._setdata,
                    "$inc": self._incdata}
        elif self._setdata and not self._incdata:
            return {"$set":self._setdata}
        elif not self._setdata and self._incdata:
            return {"$inc":self._incdata}

    def to_mongo(self):
        return self._newdata
    
    def checkNone(self):
        if self.data["username"] == "" and self.data["password"] == "":
            return True
        else:
            return False

class SensorEventCounts:

    def __init__(self,data):
        self._type = data["honeypot"]+".event.counts"
        self._date = get_date(data["timestamp"])
        self._identifier = data["identifier"]
        self._event_counts = 1
    
    def to_update(self):
        return {"$inc": {"event_counts": 1}}
    def to_mongo(self):
        return dict(type = self._type, 
                    date = self._date, 
                    identifier = self._identifier,
                    event_counts = self._event_counts)