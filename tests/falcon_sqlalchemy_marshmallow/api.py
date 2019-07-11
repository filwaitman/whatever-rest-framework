from functools import partial

from tests.falcon_sqlalchemy_marshmallow.app import User, UserSchema, session
from wrf.api.base import BaseAPI
from wrf.base import APIError
from wrf.framework.falcon import FalconFrameworkComponent
from wrf.orm.sqlalchemy import SQLAlchemyORMComponent
from wrf.pagination.base import NoPaginationComponent, PagePaginationComponent
from wrf.permission.base import AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent
from wrf.schema.marshmallow import MarshmallowSchemaComponent


class MyBaseAPI(BaseAPI):
    ORM_COMPONENT = partial(SQLAlchemyORMComponent, session=session)
    SCHEMA_COMPONENT = MarshmallowSchemaComponent
    FRAMEWORK_COMPONENT = FalconFrameworkComponent
    PAGINATION_COMPONENT = PagePaginationComponent
    PERMISSION_COMPONENT = AllowAuthenticatedPermissionComponent

    def get_current_user(self):
        return {'name': 'Filipe'}


class BaseUserAPI(MyBaseAPI):
    model_class = User
    schema_class = UserSchema

    def get_queryset(self):
        return session.query(User)

    def doublename(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        return self.framework_component.create_response({'doubled': instance.first_name * 2}, 200)

    def handled_exception(self):
        raise APIError(451, {'detail': 'Now this is a weird HTTP code'})

    def unhandled_exception(self):
        return 1 / 0


class UserOpenAPI(BaseUserAPI):
    PERMISSION_COMPONENT = AllowAllPermissionComponent


class UserReadOnlyAPI(BaseUserAPI):
    PERMISSION_COMPONENT = ReadOnlyPermissionComponent


class UserFormDataAPI(BaseUserAPI):
    FRAMEWORK_COMPONENT = partial(FalconFrameworkComponent, receive_data_as_json=False)


class UserNoPaginationAPI(BaseUserAPI):
    PAGINATION_COMPONENT = NoPaginationComponent


class UserAPI(object):
    def on_get_detail(self, req, resp, pk):
        api = BaseUserAPI(req, response=resp)
        return api.dispatch_request(api.retrieve, pk)

    def on_patch_detail(self, req, resp, pk):
        api = BaseUserAPI(req, response=resp)
        return api.dispatch_request(api.update, pk)

    def on_delete_detail(self, req, resp, pk):
        api = BaseUserAPI(req, response=resp)
        return api.dispatch_request(api.delete, pk)

    def on_get_list(self, req, resp):
        api = BaseUserAPI(req, response=resp)
        return api.dispatch_request(api.list_)

    def on_post_list(self, req, resp):
        api = BaseUserAPI(req, response=resp)
        return api.dispatch_request(api.create)

    def on_get_list_readonly(self, req, resp):
        api = UserReadOnlyAPI(req, response=resp)
        return api.dispatch_request(api.list_)

    def on_post_list_readonly(self, req, resp):
        api = UserReadOnlyAPI(req, response=resp)
        return api.dispatch_request(api.create)

    def on_get_list_no_pagination(self, req, resp):
        api = UserNoPaginationAPI(req, response=resp)
        return api.dispatch_request(api.list_)

    def on_get_list_exception_handled(self, req, resp):
        api = BaseUserAPI(req, response=resp)
        return api.dispatch_request(api.handled_exception)

    def on_get_list_exception_unhandled(self, req, resp):
        api = BaseUserAPI(req, response=resp)
        return api.dispatch_request(api.unhandled_exception)

    def on_get_detail_doublename(self, req, resp, pk):
        api = BaseUserAPI(req, response=resp)
        return api.dispatch_request(api.doublename, pk)

    def on_get_detail_doublename_open(self, req, resp, pk):
        api = UserOpenAPI(req, response=resp)
        return api.dispatch_request(api.doublename, pk)
