from functools import partial

from flask import Blueprint, request

from wrf.api.base import BaseAPI
from wrf.base import APIError
from wrf.framework.flask import FlaskFrameworkComponent
from wrf.orm.peewee import PeeweeORMComponent
from wrf.pagination.base import NoPaginationComponent, PagePaginationComponent
from wrf.permission.base import AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent
from wrf.schema.marshmallow import MarshmallowSchemaComponent

from .app import db
from .models import User
from .schemas import UserSchema

users_api_bp = Blueprint('users_api', __name__)


class MyBaseAPI(BaseAPI):
    ORM_COMPONENT = partial(PeeweeORMComponent, db=db)
    SCHEMA_COMPONENT = MarshmallowSchemaComponent
    FRAMEWORK_COMPONENT = FlaskFrameworkComponent
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


class UserFormDataAPI(UserAPI):
    FRAMEWORK_COMPONENT = partial(FlaskFrameworkComponent, receive_data_as_json=False)


class UserNoPaginationAPI(UserAPI):
    PAGINATION_COMPONENT = NoPaginationComponent


@users_api_bp.route('/', methods=['GET'])
def list_():
    api = UserAPI(request)
    return api.dispatch_request(api.list_)


@users_api_bp.route('/', methods=['POST'])
def create():
    api = UserAPI(request)
    return api.dispatch_request(api.create)


@users_api_bp.route('/<int:pk>/', methods=['GET'])
def retrieve(pk):
    api = UserAPI(request)
    return api.dispatch_request(api.retrieve, pk)


@users_api_bp.route('/<int:pk>/', methods=['PATCH'])
def update(pk):
    api = UserAPI(request)
    return api.dispatch_request(api.update, pk)


@users_api_bp.route('/<int:pk>/', methods=['DELETE'])
def delete(pk):
    api = UserAPI(request)
    return api.dispatch_request(api.delete, pk)


@users_api_bp.route('/<int:pk>/doublename/', methods=['GET'])
def doublename(pk):
    api = UserAPI(request)
    return api.dispatch_request(api.doublename, pk)


@users_api_bp.route('/<int:pk>/doublename_open/', methods=['GET'])
def open_doublename(pk):
    api = UserOpenAPI(request)
    return api.dispatch_request(api.doublename, pk)


@users_api_bp.route('/read_only/', methods=['GET', 'POST'])
def read_only_list_and_create():
    api = UserReadOnlyAPI(request)
    method = api.list_ if request.method == 'GET' else api.create
    return api.dispatch_request(method)


@users_api_bp.route('/form_data/', methods=['POST'])
def form_data_create():
    api = UserFormDataAPI(request)
    return api.dispatch_request(api.create)


@users_api_bp.route('/no_pagination/', methods=['GET'])
def no_pagination_list():
    api = UserNoPaginationAPI(request)
    return api.dispatch_request(api.list_)


@users_api_bp.route('/exception/handled/', methods=['GET'])
def handled_exception_list():
    api = UserAPI(request)
    return api.dispatch_request(api.handled_exception)


@users_api_bp.route('/exception/unhandled/', methods=['GET'])
def unhandled_exception_list():
    api = UserAPI(request)
    return api.dispatch_request(api.unhandled_exception)
