from flask import current_app
from app import db

class Condition(db.Model):

    __tablename__   = "conditions"
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(64), nullable=False)
    agent           = db.relationship('Agents', backref='condition', lazy='dynamic')
    sensor          = db.relationship('Sensor', backref='condition', lazy='dynamic')

    @staticmethod
    def insert_data():
        data = (
            (1, "Dead"),
            (2, "Paused"),
            (3, "Restarting"),
            (4, "Running"),
            (5, "Exited")
        )
        for d in data:
            cond = Condition.query.filter_by(name=d[1]).first()
            if cond is None:
                cond = Condition(name=d[1])
            db.session.add(cond)
        db.session.commit()