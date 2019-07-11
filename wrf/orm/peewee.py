from __future__ import absolute_import, division, print_function, unicode_literals

from peewee import DoesNotExist

from wrf.base import APIError

from .base import BaseORMComponent


class PeeweeORMComponent(BaseORMComponent):
    def get_queryset(self, queryset):
        return queryset

    def get_object(self, queryset, pk):
        try:
            return queryset.filter(id=pk).get()
        except DoesNotExist:
            raise APIError(404)

    def create_object(self, data):
        instance = self.context['model_class'](**data)
        instance.save()
        return instance

    def update_object(self, instance, data):
        for k, v in data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

    def delete_object(self, instance):
        instance.delete_instance()
