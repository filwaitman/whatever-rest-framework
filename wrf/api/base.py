from __future__ import absolute_import, division, print_function, unicode_literals

from functools import wraps

from wrf.base import APIError
from wrf.error.base import DefaultErrorComponent
from wrf.pagination.base import NoPaginationComponent
from wrf.permission.base import AllowAllPermissionComponent


class _Require(object):
    error_msg = 'Improperly configured: missing component "{}" configuration. Please set it in your base API class.'

    def __init__(self, name):
        self.name = name

    def __call__(self, *args, **kwargs):
        raise NotImplementedError(self.error_msg.format(self.name))


def api_view(**overrides):
    def wrap(f):
        @wraps(f)
        def wrapped_f(self, *args, **kwargs):
            self.init_context(f.__name__, **overrides)
            self.pre_request()
            try:
                response = f(self, *args, **kwargs)
                response = self.post_response(response)
                return response
            except Exception as exception:
                return self.post_exception(exception)
        return wrapped_f
    return wrap


class BaseAPI(object):
    '''
    This is the orchestrator. All your APIs shall derive from it.
    Components are usually set as a base for all APIs you're going to create. Still, you can override them to specific API needs.
    '''
    # Required
    orm_component_class = _Require('orm_component_class')
    schema_component_class = _Require('schema_component_class')
    framework_component_class = _Require('framework_component_class')

    # Optional (as they have a default set)
    error_component_class = DefaultErrorComponent
    pagination_component_class = NoPaginationComponent
    permission_component_class = AllowAllPermissionComponent

    # Required, usually specific to each API
    model_class = None
    schema_class = None

    def __init__(self, request, response=None):
        super(BaseAPI, self).__init__()
        self.request = request
        self.response = response
        self.current_user = self.get_current_user()  # TODO [later]: lazy evaluation to avoid additional queries?

    def get_orm_component_class(self, api_method_name):
        return self.orm_component_class

    def get_error_component_class(self, api_method_name):
        return self.error_component_class

    def get_schema_component_class(self, api_method_name):
        return self.schema_component_class

    def get_framework_component_class(self, api_method_name):
        return self.framework_component_class

    def get_pagination_component_class(self, api_method_name):
        return self.pagination_component_class

    def get_permission_component_class(self, api_method_name):
        return self.permission_component_class

    def init_context(self, api_method_name, **overrides):
        # if overrides:
        #     import ipdb
        #     ipdb.set_trace()
        # TODO [later]: Throttling?
        self.context = {
            # Request stuff
            'request': self.request,
            'response': self.response,
            'current_user': self.current_user,

            # Components
            'orm': overrides.get('orm_component_class', self.get_orm_component_class(api_method_name)),
            'error': overrides.get('error_component_class', self.get_error_component_class(api_method_name)),
            'schema': overrides.get('schema_component_class', self.get_schema_component_class(api_method_name)),
            'framework': overrides.get('framework_component_class', self.get_framework_component_class(api_method_name)),
            'pagination': overrides.get('pagination_component_class', self.get_pagination_component_class(api_method_name)),
            'permission': overrides.get('permission_component_class', self.get_permission_component_class(api_method_name)),

            # Other
            'model_class': self.model_class,
            'schema_class': self.schema_class,
        }

        self.orm_component = self.context['orm'](self.context)
        self.error_component = self.context['error'](self.context)
        self.schema_component = self.context['schema'](self.context)
        self.framework_component = self.context['framework'](self.context)
        self.pagination_component = self.context['pagination'](self.context)
        self.permission_component = self.context['permission'](self.context)

    def get_queryset(self):
        raise NotImplementedError()  # pragma: no cover

    def get_current_user(self):
        raise NotImplementedError()  # pragma: no cover

    def pre_request(self):
        pass

    def post_response(self, response):
        return response

    def post_exception(self, exception):
        if isinstance(exception, APIError):
            return self.error_component.handle_exception(exception)
        raise exception

    def check_permissions(self, instance=None):
        self.permission_component.check_permission(instance)

    def paginate_response(self, instances, schema=None):
        schema = schema or self.schema_component
        return self.pagination_component.paginate(schema, instances)

    def _list(self):
        self.check_permissions()
        instances = self.orm_component.get_queryset(self.get_queryset())
        return self.framework_component.create_response(self.paginate_response(instances), 200)

    def _create(self):
        self.check_permissions()
        request_data = self.framework_component.get_request_data()
        validated_data = self.schema_component.deserialize(request_data)
        instance = self.orm_component.create_object(validated_data)
        return self.framework_component.create_response(self.schema_component.serialize(instance), 201)

    def _retrieve(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        return self.framework_component.create_response(self.schema_component.serialize(instance), 200)

    def _update(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        request_data = self.framework_component.get_request_data()
        validated_data = self.schema_component.deserialize(request_data, instance=instance)
        instance = self.orm_component.update_object(instance, validated_data)
        return self.framework_component.create_response(self.schema_component.serialize(instance), 200)

    def _delete(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        self.orm_component.delete_object(instance)
        return self.framework_component.create_response(None, 204)

    @api_view()
    def list(self):
        return self._list()

    @api_view()
    def create(self):
        return self._create()

    @api_view()
    def retrieve(self, pk):
        return self._retrieve(pk)

    @api_view()
    def update(self, pk):
        return self._update(pk)

    @api_view()
    def delete(self, pk):
        return self._delete(pk)
