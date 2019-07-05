from functools import partial

from pyramid.view import view_config

from tests.pyramid_peewee_marshmallow.app import db
from tests.pyramid_peewee_marshmallow.models import User
from tests.pyramid_peewee_marshmallow.schemas import UserSchema
from wrf.api.base import BaseAPI
from wrf.base import APIError
from wrf.framework.pyramid import PyramidFrameworkComponent
from wrf.orm.peewee import PeeweeORMComponent
from wrf.pagination.base import NoPaginationComponent, PagePaginationComponent
from wrf.permission.base import AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent
from wrf.schema.marshmallow import MarshmallowSchemaComponent


class MyBaseAPI(BaseAPI):
    ORM_COMPONENT = partial(PeeweeORMComponent, db=db)
    SCHEMA_COMPONENT = MarshmallowSchemaComponent
    FRAMEWORK_COMPONENT = PyramidFrameworkComponent
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
    FRAMEWORK_COMPONENT = partial(PyramidFrameworkComponent, receive_data_as_json=False)


class UserNoPaginationAPI(UserAPI):
    PAGINATION_COMPONENT = NoPaginationComponent


@view_config(route_name='users_list', renderer='json')
def list_(request):
    api = UserAPI(request)
    return api.dispatch_request(api.list_)


@view_config(route_name='users_create', renderer='json')
def create(request):
    api = UserAPI(request)
    return api.dispatch_request(api.create)


@view_config(route_name='users_retrieve', renderer='json')
def retrieve(request):
    api = UserAPI(request)
    return api.dispatch_request(api.retrieve, request.matchdict['pk'])


@view_config(route_name='users_update', renderer='json')
def update(request):
    api = UserAPI(request)
    return api.dispatch_request(api.update, request.matchdict['pk'])


@view_config(route_name='users_delete', renderer='json')
def delete(request):
    api = UserAPI(request)
    return api.dispatch_request(api.delete, request.matchdict['pk'])


@view_config(route_name='users_doublename', renderer='json')
def doublename(request):
    api = UserAPI(request)
    return api.dispatch_request(api.doublename, request.matchdict['pk'])


@view_config(route_name='users_open_doublename', renderer='json')
def open_doublename(request):
    api = UserOpenAPI(request)
    return api.dispatch_request(api.doublename, request.matchdict['pk'])


@view_config(route_name='users_read_only_list_and_create', renderer='json')
def read_only_list_and_create(request):
    api = UserReadOnlyAPI(request)
    method = api.list_ if request.method == 'GET' else api.create
    return api.dispatch_request(method)


@view_config(route_name='users_form_data_create', renderer='json')
def form_data_create(request):
    api = UserFormDataAPI(request)
    return api.dispatch_request(api.create)


@view_config(route_name='users_no_pagination_list', renderer='json')
def no_pagination_list(request):
    api = UserNoPaginationAPI(request)
    return api.dispatch_request(api.list_)


@view_config(route_name='users_handled_exception_list', renderer='json')
def handled_exception_list(request):
    api = UserAPI(request)
    return api.dispatch_request(api.handled_exception)


@view_config(route_name='users_unhandled_exception_list', renderer='json')
def unhandled_exception_list(request):
    api = UserAPI(request)
    return api.dispatch_request(api.unhandled_exception)
