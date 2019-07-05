from datetime import datetime

from .app import db


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.now)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)

    def __repr__(self):
        return '<User: {self.first_name} {self.last_name}>'.format(self=self)
