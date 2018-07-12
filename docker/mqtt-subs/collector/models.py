
import utils
import geoip2.database
import geoip2.errors
class AttackDailyStats:
    def __init__(self,data):
        self._type          = "attack.daily.stats"
        self._identifier    = data["identifier"]
        self._date          = utils.get_date(data['timestamp'])
        self._counts        = 1
        self._hours         = utils.get_hour(data["timestamp"])
        self._hourly        = {self._hours: 1}
    
    def to_set(self):
        return {"$inc": {"counts": 1},"$set": {"hourly."+ self._hours: 1}}
    def to_inc(self):
        return {"$inc": {"counts": 1, "hourly."+ self._hours: 1}}
    def to_mongo(self):
        return dict(type        = self._type, 
                    identifier  = self._identifier,
                    date        = self._date,
                    counts      = self._counts,
                    hourly      = self._hourly)

class AttackedPortStats:
    def __init__(self,data):
        self._type          = "attacked.port.stats"
        self._identifier    = data["identifier"]
        self._date          = utils.get_date(data['timestamp'])
        self._port          = str(data["dst_port"])
        self._ports         = {str(data["dst_port"]): 1}
        
    def to_set(self):
        return {"$set": {"ports."+self._port: 1} }
    def to_inc(self):
        return {"$inc": {"ports."+self._port: 1} }
    def to_mongo(self):
        return dict(type        = self._type, 
                    date        = self._date, 
                    ports       = self._ports,
                    identifier  = self._identifier)

class CredentialCount:
    def __init__(self,mongodata,data):
        self._type          = "credential.count"
        self.mongodata      = mongodata
        self.data           = data
        self._identifier    = data["identifier"]
        self._date          = utils.get_year(data['timestamp']) if mongodata is None else mongodata['date']
        self._username_list = {} if mongodata is None or "username_list" not in mongodata else mongodata["username_list"]   
        self._password_list = {} if mongodata is None or "password_list" not in mongodata else mongodata["password_list"]
        self._newdata       = {}
        self._incdata       = {}
        self._setdata       = {}
        
        if mongodata is None:
            self._newdata = self._init_data()
        else:
            self._compute()

    def _init_data(self):
        initdata = dict(type        = self._type, 
                        date        = self._date, 
                        identifier  = self._identifier)
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

class SensorEventsCount:

    def __init__(self,data):
        self._type = "{}.events.count".format(data["sensor"])
        self._date = utils.get_date(data['timestamp'])
        self._identifier = data["identifier"]
        self._counts = 1
    
    def to_update(self):
        return {"$inc": {"counts": 1}}
        
    def to_mongo(self):
        return dict(type         = self._type, 
                    identifier   = self._identifier,
                    date         = self._date, 
                    counts       = self._counts)


class GeoIP:

    expected_attribute = ('location', 'country', 'country_code', 'state', 'city', 'postal_code', 'autonomous_system_number', 'autonomous_system_organization')

    def __init__(self, ip):
        self.ipaddr         = ip
        self.reader_city    = geoip2.database.Reader('./db/GeoLite2-City.mmdb')
        self.reader_asn     = geoip2.database.Reader('./db/GeoLite2-ASN.mmdb')
        self.addr_notfound  = False
        self.asn_notfound   = False

        try:
            self._response_city = self.reader_city.city(self.ipaddr)
            
        except geoip2.errors.AddressNotFoundError:
            self.addr_notfound = True
            self._response_city = None

        try:
            self._response_asn = self.reader_asn.asn(self.ipaddr)
            
        except geoip2.errors.AddressNotFoundError:
            self.asn_notfound = True
            self._response_asn = None
    
    def to_dict(self):
        if self.not_found():
            return None
        else:
            self.reader_city.close()
            self.reader_asn.close()

            data = dict(
                location                        = dict(
                                                    longitude=self._response_city.location.longitude,
                                                    latitude=self._response_city.location.latitude
                                                ) if self._response_city else dict(longitude=None, latitude=None),
                country                         = self._response_city.country.name if self._response_city else None,
                country_code                    = self._response_city.country.iso_code if self._response_city else None,
                state                           = self._response_city.subdivisions.most_specific.name if self._response_city else None,
                city                            = self._response_city.city.name if self._response_city else None,
                postal_code                     = self._response_city.postal.code if self._response_city else None,
                autonomous_system_organization  = self._response_asn.autonomous_system_organization if self._response_asn else None,
                autonomous_system_number        = self._response_asn.autonomous_system_number if self._response_asn else None)
            return data
    
   
    def not_found(self):
        if self.addr_notfound and self.asn_notfound:
            return True
        else:
            return False

        