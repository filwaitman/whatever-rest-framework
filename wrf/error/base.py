from __future__ import absolute_import, division, print_function, unicode_literals

from wrf.base import BaseComponent


class BaseErrorComponent(BaseComponent):
    def handle_exception(self, exception):
        raise NotImplementedError()  # pragma: no cover


class DefaultErrorComponent(BaseErrorComponent):
    def handle_exception(self, exception):
        data = {'status_code': exception.status_code}
        data.update(exception.extra)
        return self.get_instance_from_context('framework').create_response(data, exception.status_code)
