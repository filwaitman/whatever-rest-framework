from functools import partial

from flask import Blueprint, request

from wrf.api.base import BaseAPI, api_view
from wrf.base import APIError
from wrf.framework.flask import FlaskFrameworkComponent
from wrf.orm.peewee import PeeweeORMComponent
from wrf.pagination.base import NoPaginationComponent, PagePaginationComponent
from wrf.permission.base import AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent
from wrf.schema.marshmallow import MarshmallowSchemaComponent

from .models import User
from .schemas import UserSchema

users_api_bp = Blueprint('users_api', __name__)


class MyBaseAPI(BaseAPI):
    orm_component_class = PeeweeORMComponent
    schema_component_class = MarshmallowSchemaComponent
    framework_component_class = FlaskFrameworkComponent
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
        return self.framework_component.create_response({'doubled': instance.first_name * 2}, 200)

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

    @api_view(framework_component_class=partial(FlaskFrameworkComponent, receive_data_as_json=False))
    def create_formdata(self):
        return self._create()

    @api_view(pagination_component_class=NoPaginationComponent)
    def list_nopagination(self):
        return self._list()

    def get_pagination_component_class(self, api_method_name):
        if self.request.args.get('paginate') == 'f':
            return NoPaginationComponent
        return super(UserAPI, self).get_pagination_component_class(api_method_name)


@users_api_bp.route('/', methods=['GET'])
def list_():
    return UserAPI(request).list()


@users_api_bp.route('/', methods=['POST'])
def create():
    return UserAPI(request).create()


@users_api_bp.route('/<int:pk>/', methods=['GET'])
def retrieve(pk):
    return UserAPI(request).retrieve(pk)


@users_api_bp.route('/<int:pk>/', methods=['PATCH'])
def update(pk):
    return UserAPI(request).update(pk)


@users_api_bp.route('/<int:pk>/', methods=['DELETE'])
def delete(pk):
    return UserAPI(request).delete(pk)


@users_api_bp.route('/<int:pk>/doublename/', methods=['GET'])
def doublename(pk):
    return UserAPI(request).doublename(pk)


@users_api_bp.route('/<int:pk>/doublename_open/', methods=['GET'])
def open_doublename(pk):
    return UserAPI(request).doublename_open(pk)


@users_api_bp.route('/read_only/', methods=['GET', 'POST'])
def read_only_list_and_create():
    if request.method == 'GET':
        return UserAPI(request).list_readonly()
    return UserAPI(request).create_readonly()


@users_api_bp.route('/form_data/', methods=['POST'])
def form_data_create():
    return UserAPI(request).create_formdata()


@users_api_bp.route('/no_pagination/', methods=['GET'])
def no_pagination_list():
    return UserAPI(request).list_nopagination()


@users_api_bp.route('/exception/handled/', methods=['GET'])
def handled_exception_list():
    return UserAPI(request).handled_exception()


@users_api_bp.route('/exception/unhandled/', methods=['GET'])
def unhandled_exception_list():
    return UserAPI(request).unhandled_exception()
