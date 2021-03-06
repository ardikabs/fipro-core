
from flask import (
    current_app, 
    jsonify, 
    render_template, 
    request, 
    redirect, 
    url_for, 
    flash
)
from flask_login import (
    current_user,
    login_required
)
from sqlalchemy.sql import func

from app.utils import get_datetime, current_datetime
from app.commons.MongoInterface import MongoInterface as MoI
from app import db

from random import choice
import datetime
import pytz
import dateutil.parser as dateparser
import string
import requests

class Sensor(db.Model):

    __tablename__ = "sensor"
    id              = db.Column(db.Integer, primary_key=True)
    string_id       = db.Column(db.String(20))
    container_id    = db.Column(db.String(100))
    uptime          = db.Column(db.Integer, default=1)
    name            = db.Column(db.String(64), nullable=False)
    type            = db.Column(db.String(64), nullable=False)
    status          = db.Column(db.String(20), default="exited")
    registered_at   = db.Column(db.DateTime(timezone=True), default= current_datetime() )
    updated_at      = db.Column(db.DateTime(timezone=True), default= current_datetime(), onupdate= current_datetime() )
    agent_id        = db.Column(db.Integer, db.ForeignKey("agents.id"))
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"))
    condition_id    = db.Column(db.Integer, db.ForeignKey("conditions.id"), default=0)

   
    def __repr__(self):
        return '<Sensor {}-{1}>'.format(self.id, self.type)
         
    def display_uptime(self):
        intervals = (
            ('weeks', 604800),
            ('days', 86400),
            ('hours', 3600),
            ('minutes', 60),
            ('seconds', 1)
        )
        seconds = self.uptime
        for name, count in intervals:
            value = seconds // count
            if value:
                seconds = seconds - value * count
                if value == 1:
                    name = name.rstrip('s')

                return "{0} {1}".format(int(value), name)    
    

    def update(self):
        if self.condition_id != 1:
            try:
                url = "http://{0}:5000/api/v1/sensor/{1}".format(self.agent.ipaddr, self.string_id)
                req = requests.get(url, timeout=5)

                resp = req.json()
                
                if req.status_code == 404:
                    self.condition_id = 1
                    self.status = "dead"
                    setattr(self, 'attack_count', 0)
                    setattr(self, 'not_found', True)

                if resp.get('status', False):
                    print (resp.get('sensor').get('state').get('StartedAt'))
                    if resp.get('sensor').get('status') == "restarting":
                        self.uptime = 1
                    else:
                        self._set_uptime(resp.get('sensor').get('state').get('StartedAt'))

                    self._set_condition(**resp.get('sensor').get('state'))

                    self.status = resp.get('sensor').get('status')

                    moi = MoI()
                    count = moi.logs.count(identifier= self.user.identifier, agent_ip= self.agent.ipaddr, sensor= self.type)
                    setattr(self, 'attack_count', count)
                    self.attack_count = "{:,}".format(self.attack_count).replace(",",".")
        
            except Exception as e:
                print ("Error Found: {}".format(e))
                self.condition_id = 5
                self.status = "exited"
                setattr(self, 'attack_count', 0)
                setattr(self, 'error', True)

        return self

    def destroy(self):
        if self.condition_id != 1:
            try:
                url = "http://{0}:5000/api/v1/sensor/{1}/destroy".format(self.agent.ipaddr, self.string_id)
                req = requests.get(url, timeout=10)
            except requests.exceptions.ConnectionError:
                return self
        else:
            print ('Sensor {} already destroyed or dead!'.format(self.name))
            
        return self

    def _set_condition(self, **kwargs):
        if kwargs:
            expected_conditon = ('Dead', 'Paused', 'Restarting', 'Running')
            
            exited = True
            
            for cond in expected_conditon:
                if kwargs.get(cond):
                    self.condition_id = expected_conditon.index(cond) + 1
                    exited = False
            
            if exited:
                self.condition_id = 5
        else:
            raise ValueError
    
    def _set_uptime(self, started_at):
        dt_start = dateparser.parse(started_at).replace(tzinfo=pytz.utc)
        dt_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        uptime = dt_now - dt_start
        sec = 1 if abs(uptime.total_seconds()) < 1 else abs(uptime.total_seconds())
        self.uptime = sec
