from flask import current_app
from app import db


class Sensor(db.Model):

    __tablename__ = "sensor"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(64), nullable=False)
    type            = db.Column(db.String(64), nullable=False)
    status_sensor   = db.Column(db.String(10))
    registered_at   = db.Column(db.DateTime)
    last_updated_at = db.Column(db.DateTime)
    agent_id        = db.Column(db.Integer, db.ForeignKey("agents.id"))
   
    @property
    def status(self):
        return self.status
    
    @status.setter
    def status(self, status):
        self.status = status
    
    @property
    def updated_at(self):
        return self.last_updated_at
    
    @updated_at.setter
    def updated_at(self, timestamp):
        self.last_updated_at = timestamp
    
    def __repr__(self):
        return '<Agent %r>' % self.name