from __future__ import absolute_import, division, print_function, unicode_literals

from wrf.base import BaseComponent


class BaseORMComponent(BaseComponent):
    def get_queryset(self, queryset):
        raise NotImplementedError()  # pragma: no cover

    def get_object(self, queryset, pk):
        raise NotImplementedError()  # pragma: no cover

    def create_object(self, data):
        raise NotImplementedError()  # pragma: no cover

    def update_object(self, instance, data):
        raise NotImplementedError()  # pragma: no cover

    def delete_object(self, instance):
        raise NotImplementedError()  # pragma: no cover
