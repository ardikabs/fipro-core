

from flask import jsonify, render_template, redirect, url_for
from . import monitoring

@monitoring.route('/')
def index():
    return redirect(url_for('main.index'))

@monitoring.route('/top-attacks/')
def top_attacks():
    top10_asn_data = [
        {
            "asn": 15169,
            "aso": "Google LLC",
            "counts":370
        },
        {
            "asn": 7552,
            "aso": "Viettel Group",
            "counts": 129
        },
    ]

    top10_countries_data = [
        {
            "country_code": "RU",
            "country": "Russia",
            "counts": 3000
        },
        {
            "country_code": "AR",
            "country": "Argentina",
            "counts": 5000
        }
    ]

    top10_sourceip_data = [
        {
            "src_ip": "192.168.1.1",
            "country": "Russia",
            "country_code": "RU",
            "counts": 3000
        },
        {
            "src_ip": "192.168.1.3",
            "country": "Argentina",
            "country_code": "AR",
            "counts": 5000
        }
    ]

    top10_unknown_sourceip_data = [
        {
            "src_ip": "192.168.0.1",
            "counts": 3000
        },
        {
            "src_ip": "192.168.0.2",
            "counts": 5000
        }
    ]

    top_attacks_data = [
        {
            "src_ip": "192.168.1.1",
            "dst_port": 22,
            "country": "Russia",
            "country_code": "RU",
            "counts": 4500
        },
        {
            "src_ip": "192.168.1.2",
            "dst_port": 22,
            "country": "Argentina",
            "country_code": "AR",
            "counts": 300

        },
        {
            "src_ip": "192.168.1.3",
            "dst_port": 22,
            "country": "United States",
            "country_code": "US",
            "counts": 890
        }        
    ]

    data = {
        'top_attacks': top_attacks_data,
        'top10_asn': top10_asn_data,
        'top10_countries': top10_countries_data,
        'top10_sourceip': top10_sourceip_data,
        'top10_unknown_sourceip': top10_unknown_sourceip_data
    }
    return render_template('monitoring/top_attacks.html',data=data)

@monitoring.route('/event-statistics/')
def event_statistics():
    return render_template('monitoring/event_statistics.html')

@monitoring.route('/event-hourly-statistics/')
def event_hourly_statistics():
    return render_template('monitoring/event_hourly.html')


