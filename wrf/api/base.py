from __future__ import absolute_import, division, print_function, unicode_literals

from wrf.base import APIError
from wrf.error.base import DefaultErrorComponent
from wrf.pagination.base import NoPaginationComponent
from wrf.permission.base import AllowAllPermissionComponent


class BaseAPI(object):
    '''
    This is the orchestrator. All your APIs shall derive from it.
    Components are usually set as a base for all APIs you're going to create. Still, you can override them to specific API needs.
    '''
    # Required
    ORM_COMPONENT = None
    SCHEMA_COMPONENT = None
    FRAMEWORK_COMPONENT = None

    # Optional (as they have a default set)
    ERROR_COMPONENT = DefaultErrorComponent
    PAGINATION_COMPONENT = NoPaginationComponent
    PERMISSION_COMPONENT = AllowAllPermissionComponent

    # Specific to each API
    model_class = None
    schema_class = None

    def __init__(self, request):
        super(BaseAPI, self).__init__()
        self.request = request
        self.current_user = self.get_current_user()  # TODO [later]: lazy evaluation to avoid additional queries?

        orm_component = self.ORM_COMPONENT
        error_component = self.ERROR_COMPONENT
        schema_component = self.SCHEMA_COMPONENT
        framework_component = self.FRAMEWORK_COMPONENT
        pagination_component = self.PAGINATION_COMPONENT
        permission_component = self.PERMISSION_COMPONENT

        # TODO [later]: Throttling?
        self.context = {
            # Request stuff
            'request': self.request,
            'current_user': self.current_user,

            # Components
            'orm': orm_component,
            'error': error_component,
            'schema': schema_component,
            'framework': framework_component,
            'pagination': pagination_component,
            'permission': permission_component,

            # Other
            'model_class': self.model_class,
            'schema_class': self.schema_class,
        }

        self.orm_component = orm_component(self.context)
        self.error_component = error_component(self.context)
        self.schema_component = schema_component(self.context)
        self.framework_component = framework_component(self.context)
        self.pagination_component = pagination_component(self.context)
        self.permission_component = permission_component(self.context)

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

    def dispatch_request(self, method, *args, **kwargs):
        self.pre_request()
        try:
            response = method(*args, **kwargs)
            response = self.post_response(response)
            return response
        except Exception as exception:
            return self.post_exception(exception)

    def list_(self):
        self.check_permissions()
        instances = self.orm_component.get_queryset(self.get_queryset())
        return self.framework_component.create_response(self.paginate_response(instances), 200)

    def create(self):
        self.check_permissions()
        request_data = self.framework_component.get_request_data()
        validated_data = self.schema_component.deserialize(request_data)
        instance = self.orm_component.create_object(validated_data)
        return self.framework_component.create_response(self.schema_component.serialize(instance), 201)

    def retrieve(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        return self.framework_component.create_response(self.schema_component.serialize(instance), 200)

    def update(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        request_data = self.framework_component.get_request_data()
        validated_data = self.schema_component.deserialize(request_data, instance=instance)
        instance = self.orm_component.update_object(instance, validated_data)
        return self.framework_component.create_response(self.schema_component.serialize(instance), 200)

    def delete(self, pk):
        instance = self.orm_component.get_object(self.get_queryset(), pk)
        self.check_permissions(instance)
        self.orm_component.delete_object(instance)
        return self.framework_component.create_response(None, 204)
