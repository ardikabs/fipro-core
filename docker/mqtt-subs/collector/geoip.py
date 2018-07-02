import geoip2.database as db
import geoip2.errors as err

class GeoIP:

    expected_attr = ('country', 'country_code', 'location', 'state', 'city', 'postal_code', 'autonomous_system_number', 'autonomous_system_organization')
    
    def __init__(self, ipaddr=None):
        self.ipaddr = ipaddr

    def not_found(self):
        if self.addr_notfound and self.asn_notfound:
            return True  
        else:
            return False

    def _reader(self, ipaddr):
        reader_city = db.Reader('./db/GeoLite2-City.mmdb')
        reader_asn = db.Reader('./db/GeoLite2-ASN.mmdb')
        result_city = None
        result_asn = None
        try:
            result_city = reader_city.city(ipaddr)
        except err.AddressNotFoundError:
            self.addr_notfound = True
        
        try:
            result_asn = reader_asn.asn(ipaddr)
        except err.AddressNotFoundError:
            self.asn_notfound = True

        reader_city.close()
        reader_asn.close()

        return result_city, result_asn
    
    def processing(self, ipaddr):
        result_city, result_asn = self._reader(ipaddr)
        if result_city and result_asn is None:
            return None
            
        response = dict()
        if result_city:
            if result_city.location:
                location = dict(
                    latitude = result_city.location.latitude,
                    longitude = result_city.location.longitude
                )
            else:
                location = None

            response_city = dict(
                location = location,
                country = result_city.country.name,
                country_code = result_city.country.iso_code,
                state = result_city.subdivisions.most_specific.name,
                city = result_city.city.name,
                postal_code = result_city.postal.code
            )
            response.update(response_city)
        
        if result_asn:
            response_asn = dict(
                autonomous_system_number= result_asn.autonomous_system_number,
                autonomous_system_organization = result_asn.autonomous_system_organization
            )
            response.update(response_asn)
        return response

    def get_one(self, ipaddr):
        if not isinstance(ipaddr, str):
            raise TypeError("IP Address should be string")

        return self.__class__.from_response(self.processing(ipaddr), ipaddr)

    def get(self, list_ipaddr):
        if isinstance(list_ipaddr, list):
            result = list()
            for ipaddr in list_ipaddr:
                result.append(self.__class__.from_response(
                    self.processing(ipaddr), ipaddr)
                )
            return result
        
        else:
            raise TypeError

    def to_dict(self):
        todict=dict()
        for attr in self.expected_attr:
            todict.update({attr: getattr(self, attr)})
        
        return todict

    @classmethod
    def from_response(cls, dict_, ipaddr):
        
        attr = dict_.keys()
        doc = cls(ipaddr)
        for at in attr:
            if at in cls.expected_attr:
                setattr(doc, at, dict_.get(at))
        
        return doc
            