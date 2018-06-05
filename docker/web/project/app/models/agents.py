from flask import current_app
from app import db
import datetime
import string
from random import choice


el = string.ascii_letters + string.digits
rand_str = lambda n: ''.join(choice(el) for _ in range(n))

class Agents(db.Model):

    __tablename__   = "agents"
    id                  = db.Column(db.Integer, primary_key=True)
    string_id           = db.Column(db.String(32), unique=True, default=rand_str(5))
    container_id        = db.Column(db.String(100))
    name                = db.Column(db.String(64), nullable=False)
    ipaddr              = db.Column(db.String(64), nullable=False)
    registered_at       = db.Column(db.DateTime, default=datetime.datetime.now())
    status              = db.Column(db.String(10))
    user_id             = db.Column(db.Integer, db.ForeignKey("users.id"))
    sensor              = db.relationship('Sensor', backref='agent', lazy='dynamic')

    def __repr__(self):
        return '<Agent> {}'.format(self.ipaddr)
    

    @property
    def container(self):
        return self.container_id
    
    @container.setter
    def container(self, container_id):
        self.container_id =  container_id

    
    def to_dict(self):
        return dict(
            id      = self.string_id,
            name    = self.name,
            ipaddr  = self.ipaddr
        )
