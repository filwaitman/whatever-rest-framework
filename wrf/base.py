from __future__ import absolute_import, division, print_function, unicode_literals


class APIError(Exception):
    def __init__(self, status_code=400, extra=None):
        super(APIError, self).__init__()
        self.status_code = status_code
        self.extra = extra or {}


class BaseComponent(object):
    def __init__(self, context):
        super(BaseComponent, self).__init__()
        self.context = context

    def get_instance_from_context(self, name):
        return self.context[name](self.context)
