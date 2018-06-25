
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

class Agents(db.Model):

    __tablename__   = "agents"
    id              = db.Column(db.Integer, primary_key=True)
    string_id       = db.Column(db.String(20))
    container_id    = db.Column(db.String(100))
    name            = db.Column(db.String(64), nullable=False)
    uptime          = db.Column(db.Integer, default=1)
    ipaddr          = db.Column(db.String(64), nullable=False)
    registered_at   = db.Column(db.DateTime(timezone=True), default= current_datetime())
    updated_at      = db.Column(db.DateTime(timezone=True), default= current_datetime(), onupdate= current_datetime())
    status          = db.Column(db.String(10), default="exited")
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"))
    condition_id    = db.Column(db.Integer, db.ForeignKey("conditions.id"), default=5)
    sensor          = db.relationship('Sensor', backref='agent', lazy='dynamic', cascade="all, delete, delete-orphan")

    def __repr__(self):
        return '<Agent {}>'.format(self.ipaddr)

    def show_info(self):
        return '{0} ({1})'.format(self.name, self.ipaddr)

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
                if self.string_id is None:
                    url = "http://{0}:5000/api/v1/sensor/".format(self.ipaddr)
                    req = requests.get(url, {'name_container': 'fipro-agent'}, timeout=10)
                                
                else:
                    url = "http://{0}:5000/api/v1/sensor/{1}".format(self.ipaddr, self.string_id)
                    req = requests.get(url, timeout=1)
                
                resp = req.json()
                
                if req.status_code == 404:
                    self.condition_id = 5
                    self.status = "exited"
                    db.session.commit()
                    setattr(self, 'attack_count', 0)
                    setattr(self, 'not_found', True)


                if resp.get('status'):
                    self._set_uptime(resp.get('sensor').get('state').get('StartedAt'))
                    self._set_condition(**resp.get('sensor').get('state'))

                    self.string_id = resp.get('sensor').get('short_id')
                    self.container_id = resp.get('sensor').get('id')
                    self.status = resp.get('sensor').get('status')
                db.session.commit()

                moi = MoI("mongodb://192.168.1.100:27017/")
                count = moi.logs.count(identifier= current_user.identifier, agent_ip= self.ipaddr)
                setattr(self, 'attack_count', count)
                self.attack_count = "{:,}".format(self.attack_count).replace(",",".")

            except:
                self.condition_id = 5
                self.status = "exited"
                db.session.commit()
                setattr(self, 'attack_count', 0)
                setattr(self, 'error', True)
            
        return self

    
    def destroy(self):
        try:
            url = "http://{0}:5000/api/v1/sensor/{1}/destroy".format(self.agent.ipaddr, self.string_id)
            req = requests.get(url, timeout=10)
        except ConnectionError:
            return self
            
        return self

    def to_dict(self):
        return dict(
            id      = self.string_id,
            name    = self.name,
            ipaddr  = self.ipaddr
        )


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
        self.uptime = uptime.total_seconds()