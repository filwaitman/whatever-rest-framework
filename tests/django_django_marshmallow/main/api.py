from functools import partial

from django.views.generic import View

from wrf.api.base import BaseAPI, api_view
from wrf.base import APIError
from wrf.framework.django import DjangoFrameworkComponent
from wrf.orm.django import DjangoORMComponent
from wrf.pagination.base import NoPaginationComponent, PagePaginationComponent
from wrf.permission.base import AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent
from wrf.schema.marshmallow import MarshmallowSchemaComponent

from .models import User
from .schemas import UserSchema


class MyBaseAPI(BaseAPI):
    orm_component_class = DjangoORMComponent
    schema_component_class = MarshmallowSchemaComponent
    framework_component_class = DjangoFrameworkComponent
    pagination_component_class = PagePaginationComponent
    permission_component_class = AllowAuthenticatedPermissionComponent

    def get_current_user(self):
        # `bool(request.user)` is `True` for unauthenticated users. Shame on django.
        return self.request.user if self.request.user.is_authenticated else None


class UserAPI(MyBaseAPI):
    model_class = User
    schema_class = UserSchema

    def get_queryset(self):
        return User.objects.all()

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

    @api_view(framework_component_class=partial(DjangoFrameworkComponent, receive_data_as_json=False))
    def create_formdata(self):
        return self._create()

    @api_view(pagination_component_class=NoPaginationComponent)
    def list_nopagination(self):
        return self._list()

    def get_pagination_component_class(self, api_method_name):
        if self.request.GET.get('paginate') == 'f':
            return NoPaginationComponent
        return super(UserAPI, self).get_pagination_component_class(api_method_name)


class CustomDispatchMixin(object):
    def dispatch(self, request, *args, **kwargs):
        custom = '{}_{}'.format(request.method.lower(), kwargs['action'])
        custom_method = getattr(self, custom, None)
        if custom_method:
            return custom_method(request, *args, **kwargs)
        return super(CustomDispatchMixin, self).dispatch(request, *args, **kwargs)


class UserListAPI(View):
    def get(self, request, *args, **kwargs):
        return UserAPI(request).list()

    def post(self, request, *args, **kwargs):
        return UserAPI(request).create()


class UserListCustomAPI(CustomDispatchMixin, View):
    def get_read_only(self, request, *args, **kwargs):
        return UserAPI(request).list_readonly()

    def post_read_only(self, request, *args, **kwargs):
        return UserAPI(request).create_readonly()

    def get_no_pagination(self, request, *args, **kwargs):
        return UserAPI(request).list_nopagination()

    def get_exception_handled(self, request, *args, **kwargs):
        return UserAPI(request).handled_exception()

    def get_exception_unhandled(self, request, *args, **kwargs):
        return UserAPI(request).unhandled_exception()

    def post_form_data(self, request, *args, **kwargs):
        return UserAPI(request).create_formdata()


class UserDetailAPI(View):
    def get(self, request, pk, *args, **kwargs):
        return UserAPI(request).retrieve(pk)

    def patch(self, request, pk, *args, **kwargs):
        return UserAPI(request).update(pk)

    def delete(self, request, pk, *args, **kwargs):
        return UserAPI(request).delete(pk)


class UserDetailCustomAPI(CustomDispatchMixin, View):
    def get_doublename(self, request, pk, *args, **kwargs):
        return UserAPI(request).doublename(pk)

    def get_doublename_open(self, request, pk, *args, **kwargs):
        return UserAPI(request).doublename_open(pk)
