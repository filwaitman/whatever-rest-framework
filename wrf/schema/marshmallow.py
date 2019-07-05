from __future__ import absolute_import, division, print_function, unicode_literals

from wrf.base import APIError

from .base import BaseSchemaComponent


class MarshmallowSchemaComponent(BaseSchemaComponent):
    def deserialize(self, data, instance=None):
        partial = bool(instance)
        unmarshal_result = self.context['schema_class'](partial=partial).load(data)
        if unmarshal_result.errors:
            raise APIError(400, extra=unmarshal_result.errors)

        return unmarshal_result.data

    def serialize(self, instance_or_queryset, many=False):
        return self.context['schema_class'](many=many).dump(instance_or_queryset).data
