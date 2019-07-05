from __future__ import absolute_import, division, print_function, unicode_literals

import json

from chalice import Response

from wrf.compat import JSONDecodeError, urlencode

from .base import BaseFrameworkComponent


class ChaliceFrameworkComponent(BaseFrameworkComponent):
    def get_request_data(self):
        try:
            return json.loads(self.context['request'].raw_body.decode('utf-8'))
        except JSONDecodeError:
            return {}

    def get_request_query(self):
        return self.context['request'].query_params or {}

    def get_request_method(self):
        return self.context['request'].method

    def get_request_url(self):
        request_dict = self.context['request'].to_dict()
        query_params = urlencode(self.get_request_query())
        url = '{}{}'.format('', request_dict['context']['resourcePath'])  # TODO [later]: add base url
        if query_params:
            url += '?{}'.format(query_params)
        return url

    def create_response(self, data, status_code):
        return Response(body=json.dumps(data), status_code=status_code)
