from __future__ import absolute_import, division, print_function, unicode_literals

from paginate import Page

from wrf.base import BaseComponent
from wrf.compat import parse_qsl, urlencode, urlparse, urlunparse


class BasePaginationComponent(BaseComponent):
    def paginate(self, schema, instances):
        raise NotImplementedError()  # pragma: no cover


class NoPaginationComponent(BasePaginationComponent):
    def paginate(self, schema, instances):
        return schema.serialize(instances, many=True)


class OrmWrapper(object):
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, range):
        return self.obj[range]

    def __len__(self):
        return self.obj.count()


class OrmPage(Page):
    def __init__(self, *args, **kwargs):
        super(OrmPage, self).__init__(*args, wrapper_class=OrmWrapper, **kwargs)


class PagePaginationComponent(BasePaginationComponent):
    def __init__(self, context, default_per_page=10, page_param='page', per_page_param='per_page'):
        super(PagePaginationComponent, self).__init__(context)
        self.default_per_page = default_per_page
        self.page_param = page_param
        self.per_page_param = per_page_param

    def _add_querystring_to_url(self, url, **params):
        url_parts = list(urlparse(url))
        query = dict(parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urlencode(query)
        return urlunparse(url_parts)

    def _get_page_number(self, request_query):
        try:
            return int(request_query.get(self.page_param))
        except (TypeError, ValueError):
            return 1

    def _get_items_per_page(self, request_query):
        try:
            return int(request_query.get(self.per_page_param))
        except (TypeError, ValueError):
            return self.default_per_page

    def paginate(self, schema, instances):
        framework = self.get_instance_from_context('framework')
        request_query = framework.get_request_query()
        request_url = framework.get_request_url()

        page = OrmPage(instances, self._get_page_number(request_query), self._get_items_per_page(request_query))

        return {
            'count': page.item_count,
            'next_page': self._add_querystring_to_url(request_url, page=page.next_page) if page.next_page else None,
            'prev_page': self._add_querystring_to_url(request_url, page=page.previous_page) if page.previous_page else None,
            'results': schema.serialize(page.items, many=True),
        }
