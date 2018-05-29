from flask import current_app
from app import db
import datetime

class Agents(db.Model):

    __tablename__   = "agents"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(64), nullable=False)
    ipaddr          = db.Column(db.String(64), nullable=False)
    registered_at   = db.Column(db.DateTime, default=datetime.datetime.today())
    status          = db.Column(db.String(10))
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"))
    sensor          = db.relationship('Sensor', backref='agent', lazy='dynamic')

    def __repr__(self):
        return '<Agent> {}'.format(self.ipaddr)
    
    def to_dict(self):
        return dict(
            name    = self.name,
            ipaddr  = self.ipaddr
        )
