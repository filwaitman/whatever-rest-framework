from __future__ import absolute_import, division, print_function, unicode_literals

from flask import jsonify

from .base import BaseFrameworkComponent


class FlaskFrameworkComponent(BaseFrameworkComponent):
    def __init__(self, context, receive_data_as_json=True):
        super(FlaskFrameworkComponent, self).__init__(context)
        self.receive_data_as_json = receive_data_as_json

    def get_request_data(self):
        if self.receive_data_as_json:
            return self.context['request'].json or {}
        return self.context['request'].form or {}

    def get_request_query(self):
        return self.context['request'].args or {}

    def get_request_method(self):
        return self.context['request'].method

    def get_request_url(self):
        return self.context['request'].url

    def create_response(self, data, status_code):
        return jsonify(data), status_code
