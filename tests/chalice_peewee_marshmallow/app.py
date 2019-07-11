from datetime import datetime

from chalice import Chalice
from marshmallow import Schema, fields, validate
from peewee import CharField, DateTimeField, Model, SqliteDatabase

from wrf.api.base import BaseAPI
from wrf.base import APIError
from wrf.framework.chalice import ChaliceFrameworkComponent
from wrf.orm.peewee import PeeweeORMComponent
from wrf.pagination.base import NoPaginationComponent, PagePaginationComponent
from wrf.permission.base import AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent
from wrf.schema.marshmallow import MarshmallowSchemaComponent

db = SqliteDatabase(':memory:')
app = Chalice(app_name='wrf')


class UserSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(1))
    last_name = fields.String(required=True, validate=validate.Length(1))

    class Meta:
        dump_only = ('id', 'created')
        fields = dump_only + ('first_name', 'last_name')


class User(Model):
    __tablename__ = 'user'

    created = DateTimeField(default=datetime.now)
    first_name = CharField()
    last_name = CharField()

    class Meta:
        database = db

    def __repr__(self):
        return '<User: {self.first_name} {self.last_name}>'.format(self=self)


class MyBaseAPI(BaseAPI):
    ORM_COMPONENT = PeeweeORMComponent
    SCHEMA_COMPONENT = MarshmallowSchemaComponent
    FRAMEWORK_COMPONENT = ChaliceFrameworkComponent
    PAGINATION_COMPONENT = PagePaginationComponent
    PERMISSION_COMPONENT = AllowAuthenticatedPermissionComponent

    def get_current_user(self):
        return {'name': 'Filipe'}


class UserAPI(MyBaseAPI):
    model_class = User
    schema_class = UserSchema

    def get_queryset(self):
        return User.select()

    def doublename(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        return self.framework_component.create_response({'doubled': instance.first_name * 2}, 200)

    def handled_exception(self):
        raise APIError(499, {'detail': 'Now this is a weird HTTP code'})

    def unhandled_exception(self):
        return 1 / 0


class UserOpenAPI(UserAPI):
    PERMISSION_COMPONENT = AllowAllPermissionComponent


class UserReadOnlyAPI(UserAPI):
    PERMISSION_COMPONENT = ReadOnlyPermissionComponent


class UserNoPaginationAPI(UserAPI):
    PAGINATION_COMPONENT = NoPaginationComponent


@app.route('/api/users', methods=['GET'])
def list_():
    db.create_tables([User])
    api = UserAPI(app.current_request)
    return api.dispatch_request(api.list_)


@app.route('/api/users', methods=['POST'])
def create():
    db.create_tables([User])
    api = UserAPI(app.current_request)
    return api.dispatch_request(api.create)


@app.route('/api/users/{pk}', methods=['GET'])
def retrieve(pk):
    db.create_tables([User])
    api = UserAPI(app.current_request)
    return api.dispatch_request(api.retrieve, pk)


@app.route('/api/users/{pk}', methods=['PATCH'])
def update(pk):
    db.create_tables([User])
    api = UserAPI(app.current_request)
    return api.dispatch_request(api.update, pk)


@app.route('/api/users/{pk}', methods=['DELETE'])
def delete(pk):
    db.create_tables([User])
    api = UserAPI(app.current_request)
    return api.dispatch_request(api.delete, pk)


@app.route('/api/users/{pk}/doublename', methods=['GET'])
def doublename(pk):
    db.create_tables([User])
    api = UserAPI(app.current_request)
    return api.dispatch_request(api.doublename, pk)


@app.route('/api/users/{pk}/doublename_open', methods=['GET'])
def open_doublename(pk):
    db.create_tables([User])
    api = UserOpenAPI(app.current_request)
    return api.dispatch_request(api.doublename, pk)


@app.route('/api/users/read_only', methods=['GET', 'POST'])
def read_only_list_and_create():
    db.create_tables([User])
    api = UserReadOnlyAPI(app.current_request)
    method = api.list_ if app.current_request.method == 'GET' else api.create
    return api.dispatch_request(method)


@app.route('/api/users/no_pagination', methods=['GET'])
def no_pagination_list():
    db.create_tables([User])
    api = UserNoPaginationAPI(app.current_request)
    return api.dispatch_request(api.list_)


@app.route('/api/users/exception/handled', methods=['GET'])
def handled_exception_list():
    db.create_tables([User])
    api = UserAPI(app.current_request)
    return api.dispatch_request(api.handled_exception)


@app.route('/api/users/exception/unhandled', methods=['GET'])
def unhandled_exception_list():
    db.create_tables([User])
    api = UserAPI(app.current_request)
    return api.dispatch_request(api.unhandled_exception)
