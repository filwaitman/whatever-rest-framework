from functools import partial

from tests.falcon_sqlalchemy_marshmallow.app import User, UserSchema, session
from wrf.api.base import BaseAPI, api_view
from wrf.base import APIError
from wrf.framework.falcon import FalconFrameworkComponent
from wrf.orm.sqlalchemy import SQLAlchemyORMComponent
from wrf.pagination.base import NoPaginationComponent, PagePaginationComponent
from wrf.permission.base import AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent
from wrf.schema.marshmallow import MarshmallowSchemaComponent


class MyBaseAPI(BaseAPI):
    orm_component_class = partial(SQLAlchemyORMComponent, session=session)
    schema_component_class = MarshmallowSchemaComponent
    framework_component_class = FalconFrameworkComponent
    pagination_component_class = PagePaginationComponent
    permission_component_class = AllowAuthenticatedPermissionComponent

    def get_current_user(self):
        return {'name': 'Filipe'}


class BaseUserAPI(MyBaseAPI):
    model_class = User
    schema_class = UserSchema

    def get_queryset(self):
        return session.query(User)

    def _doublename(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        return self.framework_component.create_response({'doubled': instance.first_name * 2}, 200)

    @api_view()
    def doublename(self, pk):
        return self._doublename(pk)

    @api_view()
    def handled_exception(self):
        raise APIError(451, {'detail': 'Now this is a weird HTTP code'})

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
        if self.request.params.get('paginate') == 'f':
            return NoPaginationComponent
        return super(BaseUserAPI, self).get_pagination_component_class(api_method_name)


class UserAPI(object):
    def on_get_detail(self, req, resp, pk):
        return BaseUserAPI(req, response=resp).retrieve(pk)

    def on_patch_detail(self, req, resp, pk):
        return BaseUserAPI(req, response=resp).update(pk)

    def on_delete_detail(self, req, resp, pk):
        return BaseUserAPI(req, response=resp).delete(pk)

    def on_get_list(self, req, resp):
        return BaseUserAPI(req, response=resp).list()

    def on_post_list(self, req, resp):
        return BaseUserAPI(req, response=resp).create()

    def on_get_list_readonly(self, req, resp):
        return BaseUserAPI(req, response=resp).list_readonly()

    def on_post_list_readonly(self, req, resp):
        return BaseUserAPI(req, response=resp).create_readonly()

    def on_get_list_no_pagination(self, req, resp):
        return BaseUserAPI(req, response=resp).list_nopagination()

    def on_get_list_exception_handled(self, req, resp):
        return BaseUserAPI(req, response=resp).handled_exception()

    def on_get_list_exception_unhandled(self, req, resp):
        return BaseUserAPI(req, response=resp).unhandled_exception()

    def on_get_detail_doublename(self, req, resp, pk):
        return BaseUserAPI(req, response=resp).doublename(pk)

    def on_get_detail_doublename_open(self, req, resp, pk):
        return BaseUserAPI(req, response=resp).doublename_open(pk)
