

from flask import jsonify, render_template
from . import logs

@logs.route('/')
def index():
    return render_template('logs/index.html')

@logs.route('/dionaea/')
def dionaea_index():
    return render_template('logs/dionaea_index.html')
    
@logs.route('/cowrie/')
def cowrie_index():
    data = [
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c16acd56",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c16acd56",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c16acd57",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c16acd57",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c16acd58",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c16acd58",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
            {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c26acd58",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c26acd58",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c18cd58",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c18acd58",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c16ace58",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        },
        {
            "eventid": "cowrie.session.connect",
            "src_ip": "127.0.0.1",
            "dst_ip": "192.168.1.0",
            "dst_port": "22",
            "session": "c16ace58",
            "message": "New connection: 127.0.0.1:43963 (127.0.0.1:2299) [session: c16acd56]",
            "location": "(55.1544, 61.4297)",
            "country": "Russia",
            "country_code": "RU",
            "state": "Chelyabinsk",
            "city": "Chelyabinsk",
            "postal_code": "454008",
            "asn": "8369",
            "aso": "Intersvyaz-2 JSC",
            "timestamp": "2017-04-03 21:07:07.319Z"
        }
    ]
    return render_template('logs/cowrie_index.html',data=data)

@logs.route('/glastopf/')
def glastopf_index():
    return render_template('logs/glastopf_index.html')


@logs.route('/cowrie/<string:session>/')
def cowrie_item(session):
    return render_template('logs/cowrie_item.html')