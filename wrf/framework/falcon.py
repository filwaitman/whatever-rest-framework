from __future__ import absolute_import, division, print_function, unicode_literals

import falcon

from .base import BaseFrameworkComponent


class FalconFrameworkComponent(BaseFrameworkComponent):
    def __init__(self, context):
        super(FalconFrameworkComponent, self).__init__(context)
        assert self.context['response'] is not None  # TODO: better error message

    def _get_status_code_as_falcon_attribute(self, int_status_code):
        return getattr(falcon, 'HTTP_{}'.format(int_status_code))

    def get_request_data(self):
        return self.context['request'].media or {}

    def get_request_query(self):
        return self.context['request'].params or {}

    def get_request_method(self):
        return self.context['request'].method

    def get_request_url(self):
        url = self.context['request'].url

        query = self.context['request'].query_string
        if query:
            url = '{}?{}'.format(url, query)

        return url

    def create_response(self, data, status_code, headers=None):
        headers = headers or {}
        for key, value in headers.items():
            self.context['response'].append_header(key, value)
        self.context['response'].media = data
        self.context['response'].status = self._get_status_code_as_falcon_attribute(status_code)
