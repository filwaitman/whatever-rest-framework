from __future__ import absolute_import, division, print_function, unicode_literals

from wrf.base import BaseComponent


class BaseFrameworkComponent(BaseComponent):
    def get_request_data(self):
        raise NotImplementedError()  # pragma: no cover

    def get_request_query(self):
        raise NotImplementedError()  # pragma: no cover

    def get_request_method(self):
        raise NotImplementedError()  # pragma: no cover

    def get_request_url(self):
        raise NotImplementedError()  # pragma: no cover

    def create_response(self, data, status_code):
        raise NotImplementedError()  # pragma: no cover
