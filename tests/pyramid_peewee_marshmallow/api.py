from functools import partial

from pyramid.view import view_config

from tests.pyramid_peewee_marshmallow.models import User
from tests.pyramid_peewee_marshmallow.schemas import UserSchema
from wrf.api.base import BaseAPI, api_view
from wrf.base import APIError
from wrf.framework.pyramid import PyramidFrameworkComponent
from wrf.orm.peewee import PeeweeORMComponent
from wrf.pagination.base import NoPaginationComponent, PagePaginationComponent
from wrf.permission.base import AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent
from wrf.schema.marshmallow import MarshmallowSchemaComponent


class MyBaseAPI(BaseAPI):
    orm_component_class = PeeweeORMComponent
    schema_component_class = MarshmallowSchemaComponent
    framework_component_class = PyramidFrameworkComponent
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

    @api_view(framework_component_class=partial(PyramidFrameworkComponent, receive_data_as_json=False))
    def create_formdata(self):
        return self._create()

    @api_view(pagination_component_class=NoPaginationComponent)
    def list_nopagination(self):
        return self._list()

    def get_pagination_component_class(self, api_method_name):
        if self.request.params.get('paginate') == 'f':
            return NoPaginationComponent
        return super(UserAPI, self).get_pagination_component_class(api_method_name)


@view_config(route_name='users_list', renderer='json')
def list(request):
    return UserAPI(request).list()


@view_config(route_name='users_create', renderer='json')
def create(request):
    return UserAPI(request).create()


@view_config(route_name='users_retrieve', renderer='json')
def retrieve(request):
    return UserAPI(request).retrieve(request.matchdict['pk'])


@view_config(route_name='users_update', renderer='json')
def update(request):
    return UserAPI(request).update(request.matchdict['pk'])


@view_config(route_name='users_delete', renderer='json')
def delete(request):
    return UserAPI(request).delete(request.matchdict['pk'])


@view_config(route_name='users_doublename', renderer='json')
def doublename(request):
    return UserAPI(request).doublename(request.matchdict['pk'])


@view_config(route_name='users_open_doublename', renderer='json')
def open_doublename(request):
    return UserAPI(request).doublename_open(request.matchdict['pk'])


@view_config(route_name='users_read_only_list_and_create', renderer='json')
def read_only_list_and_create(request):
    if request.method == 'GET':
        return UserAPI(request).list_readonly()
    return UserAPI(request).create_readonly()


@view_config(route_name='users_form_data_create', renderer='json')
def form_data_create(request):
    return UserAPI(request).create_formdata()


@view_config(route_name='users_no_pagination_list', renderer='json')
def no_pagination_list(request):
    return UserAPI(request).list_nopagination()


@view_config(route_name='users_handled_exception_list', renderer='json')
def handled_exception_list(request):
    return UserAPI(request).handled_exception()


@view_config(route_name='users_unhandled_exception_list', renderer='json')
def unhandled_exception_list(request):
    return UserAPI(request).unhandled_exception()
