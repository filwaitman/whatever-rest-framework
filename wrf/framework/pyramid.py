from __future__ import absolute_import, division, print_function, unicode_literals

from pyramid.httpexceptions import HTTPNoContent

from wrf.compat import JSONDecodeError

from .base import BaseFrameworkComponent


class PyramidFrameworkComponent(BaseFrameworkComponent):
    def __init__(self, context, receive_data_as_json=True):
        super(PyramidFrameworkComponent, self).__init__(context)
        self.receive_data_as_json = receive_data_as_json

    def get_request_data(self):
        if self.receive_data_as_json:
            try:
                return self.context['request'].json_body or {}
            except JSONDecodeError:
                # TODO [later]: Add a warning here?
                return {}

        return self.context['request'].POST or {}

    def get_request_query(self):
        return self.context['request'].params or {}

    def get_request_method(self):
        return self.context['request'].method

    def get_request_url(self):
        return '{}{}'.format(self.context['request'].host_url, self.context['request'].path_qs)

    def create_response(self, data, status_code):
        if status_code == 204:
            raise HTTPNoContent()  # See https://github.com/Pylons/pyramid/issues/709
        self.context['request'].response.status = status_code
        return data
