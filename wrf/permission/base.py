from __future__ import absolute_import, division, print_function, unicode_literals

from wrf.base import APIError, BaseComponent


class BasePermissionComponent(BaseComponent):
    def check_permission(self, instance=None):
        raise NotImplementedError()  # pragma: no cover


class AllowAllPermissionComponent(BasePermissionComponent):
    def check_permission(self, instance=None):
        pass


class AllowAuthenticatedPermissionComponent(BasePermissionComponent):
    def check_permission(self, instance=None):
        if self.context['current_user'] is None:
            raise APIError(401)


class ReadOnlyPermissionComponent(BasePermissionComponent):
    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')

    def check_permission(self, instance=None):
        if self.get_instance_from_context('framework').get_request_method() not in self.SAFE_METHODS:
            raise APIError(403)
