from __future__ import absolute_import, division, print_function, unicode_literals

from sqlalchemy.orm.exc import NoResultFound

from wrf.base import APIError

from .base import BaseORMComponent


class SQLAlchemyORMComponent(BaseORMComponent):
    def __init__(self, context, db, commit=True):
        super(SQLAlchemyORMComponent, self).__init__(context)
        self.db = db
        self.commit = commit

    def get_queryset(self, queryset):
        return queryset

    def get_object(self, queryset, pk):
        try:
            return queryset.filter_by(id=pk).one()
        except NoResultFound:
            raise APIError(404)

    def _maybe_commit(self):
        if self.commit:
            self.db.session.commit()

    def create_object(self, data):
        model_class = self.context['model_class']
        # Marshmallow-SQLAlchemy transforms the schema results into a instance, that's why we have the conditional below
        instance = data if isinstance(data, model_class) else model_class(**data)

        self.db.session.add(instance)
        self._maybe_commit()
        return instance

    def update_object(self, instance, data):
        self.db.session.add(instance)
        self._maybe_commit()
        return instance

    def delete_object(self, instance):
        self.db.session.delete(instance)
        self._maybe_commit()
