from datetime import datetime

from chalice import Chalice
from marshmallow import Schema, fields, validate
from peewee import CharField, DateTimeField, Model, SqliteDatabase

from wrf.api.base import BaseAPI, api_view
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
    orm_component_class = PeeweeORMComponent
    schema_component_class = MarshmallowSchemaComponent
    framework_component_class = ChaliceFrameworkComponent
    pagination_component_class = PagePaginationComponent
    permission_component_class = AllowAuthenticatedPermissionComponent

    def get_current_user(self):
        return {'name': 'Filipe'}


class UserAPI(MyBaseAPI):
    model_class = User
    schema_class = UserSchema

    def get_queryset(self):
        return User.select()

    def _doublename(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        data = {'doubled': instance.first_name * 2}
        return self.framework_component.create_response(data, 200, headers={'header-passed-in': '1'})

    @api_view()
    def doublename(self, pk):
        return self._doublename(pk)

    @api_view()
    def handled_exception(self):
        raise APIError(499, {'detail': 'Now this is a weird HTTP code'})

    @api_view()
    def unhandled_exception(self):
        return 1 / 0

    @api_view(permission_component_class=AllowAllPermissionComponent)
    def doublename_open(self, pk):
        return self._doublename(pk)

    @api_view(permission_component_class=ReadOnlyPermissionComponent)
    def list_readonly(self):
        return self._list()

    @api_view(permission_component_class=ReadOnlyPermissionComponent)
    def create_readonly(self):
        return self._create()

    @api_view(pagination_component_class=NoPaginationComponent)
    def list_nopagination(self):
        return self._list()

    def get_pagination_component_class(self, api_method_name):
        if self.request.query_params.get('paginate') == 'f':
            return NoPaginationComponent
        return super(UserAPI, self).get_pagination_component_class(api_method_name)


@app.route('/api/users', methods=['GET'])
def list():
    db.create_tables([User])
    return UserAPI(app.current_request).list()


@app.route('/api/users', methods=['POST'])
def create():
    db.create_tables([User])
    return UserAPI(app.current_request).create()


@app.route('/api/users/{pk}', methods=['GET'])
def retrieve(pk):
    db.create_tables([User])
    return UserAPI(app.current_request).retrieve(pk)


@app.route('/api/users/{pk}', methods=['PATCH'])
def update(pk):
    db.create_tables([User])
    return UserAPI(app.current_request).update(pk)


@app.route('/api/users/{pk}', methods=['DELETE'])
def delete(pk):
    db.create_tables([User])
    return UserAPI(app.current_request).delete(pk)


@app.route('/api/users/{pk}/doublename', methods=['GET'])
def doublename(pk):
    db.create_tables([User])
    return UserAPI(app.current_request).doublename(pk)


@app.route('/api/users/{pk}/doublename_open', methods=['GET'])
def open_doublename(pk):
    db.create_tables([User])
    return UserAPI(app.current_request).doublename_open(pk)


@app.route('/api/users/read_only', methods=['GET', 'POST'])
def read_only_list_and_create():
    db.create_tables([User])
    if app.current_request.method == 'GET':
        return UserAPI(app.current_request).list_readonly()
    return UserAPI(app.current_request).create_readonly()


@app.route('/api/users/no_pagination', methods=['GET'])
def no_pagination_list():
    db.create_tables([User])
    return UserAPI(app.current_request).list_nopagination()


@app.route('/api/users/exception/handled', methods=['GET'])
def handled_exception_list():
    db.create_tables([User])
    return UserAPI(app.current_request).handled_exception()


@app.route('/api/users/exception/unhandled', methods=['GET'])
def unhandled_exception_list():
    db.create_tables([User])
    return UserAPI(app.current_request).unhandled_exception()
