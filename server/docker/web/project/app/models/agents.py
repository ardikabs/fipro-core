from flask import current_app
from app import db


class Agent(db.Model):

    __tablename__ = "agents"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(64), nullable=False)
    ipaddr          = db.Column(db.String(64), nullable=False)
    registered_at   = db.Column(db.DateTime)
    status          = db.Column(db.String(10))
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"))
    sensor          = db.relationship('Sensor', backref='agent', lazy='dynamic')

    def __repr__(self):
        return '<Agent %r>' % self.ipaddr
    
