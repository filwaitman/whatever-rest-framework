from __future__ import absolute_import, division, print_function, unicode_literals

from wrf.base import BaseComponent


class BaseSchemaComponent(BaseComponent):
    def deserialize(self, data, instance=None):
        raise NotImplementedError()  # pragma: no cover

    def serialize(self, instance_or_queryset, many=False):
        raise NotImplementedError()  # pragma: no cover
