import logging
from datetime import datetime

import falcon
from marshmallow import Schema, fields, validate
from sqlalchemy import Column, DateTime, Integer, MetaData, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

logger = logging.getLogger('gunicorn.error')
engine = create_engine('sqlite://')
Base = declarative_base(metadata=MetaData(bind=engine))
session = Session(engine)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    first_name = Column(String)
    last_name = Column(String)

    def __repr__(self):
        return '<User: {self.first_name} {self.last_name}>'.format(self=self)


class UserSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(1))
    last_name = fields.String(required=True, validate=validate.Length(1))

    class Meta:
        dump_only = ('id', 'created')
        fields = dump_only + ('first_name', 'last_name')


class ResponseLoggerMiddleware(object):
    def process_response(self, req, resp, resource, req_succeeded):
        logger.info('{0} {1} {2}'.format(req.method, req.relative_uri, resp.status[:3]))


def create_app():
    from tests.falcon_sqlalchemy_marshmallow.api import UserAPI

    api = falcon.API(middleware=[ResponseLoggerMiddleware()])
    user_api = UserAPI()

    api.add_route('/api/users', user_api, suffix='list')
    api.add_route('/api/users/read_only', user_api, suffix='list_readonly')
    api.add_route('/api/users/no_pagination', user_api, suffix='list_no_pagination')
    api.add_route('/api/users/exception/handled', user_api, suffix='list_exception_handled')
    api.add_route('/api/users/exception/unhandled', user_api, suffix='list_exception_unhandled')
    api.add_route('/api/users/{pk}', user_api, suffix='detail')
    api.add_route('/api/users/{pk}/doublename', user_api, suffix='detail_doublename')
    api.add_route('/api/users/{pk}/doublename_open', user_api, suffix='detail_doublename_open')

    return api


Base.metadata.create_all(engine)
assert User.__table__.exists()
