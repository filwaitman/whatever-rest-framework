from datetime import datetime

from peewee import CharField, DateTimeField, Model

from .app import db


class User(Model):
    __tablename__ = 'user'

    created = DateTimeField(default=datetime.now)
    first_name = CharField()
    last_name = CharField()

    class Meta:
        database = db

    def __repr__(self):
        return '<User: {self.first_name} {self.last_name}>'.format(self=self)
