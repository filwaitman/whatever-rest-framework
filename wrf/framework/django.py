from __future__ import absolute_import, division, print_function, unicode_literals

import json

from django.http import HttpResponse, JsonResponse

from wrf.compat import JSONDecodeError

from .base import BaseFrameworkComponent


class DjangoFrameworkComponent(BaseFrameworkComponent):
    def __init__(self, context, receive_data_as_json=True):
        super(DjangoFrameworkComponent, self).__init__(context)
        self.receive_data_as_json = receive_data_as_json

    def get_request_data(self):
        if not self.receive_data_as_json:
            return dict(self.context['request'].POST.items())
        try:
            return json.loads(self.context['request'].body.decode('utf-8'))
        except JSONDecodeError:
            return {}

    def get_request_query(self):
        return self.context['request'].GET or {}

    def get_request_method(self):
        return self.context['request'].method

    def get_request_url(self):
        return self.context['request'].build_absolute_uri()

    def create_response(self, data, status_code, headers=None):
        if status_code == 204:
            response = HttpResponse(status=204)
        else:
            response = JsonResponse(data, status=status_code, safe=False)

        headers = headers or {}
        for key, value in headers.items():
            response[key] = value

        return response
