from flask import jsonify, request


class FrameworkInterface(object):
    @classmethod
    def get_request_data(cls, request):
        return request.json


class ORMInterface(object):
    @classmethod
    def get_queryset(cls, queryset):
        pass

    @classmethod
    def get_object(cls, queryset, pk):
        pass

    @classmethod
    def create_object(cls, model, data):
        pass

    @classmethod
    def update_object(cls, instance, data):
        pass

    @classmethod
    def delete_object(cls, instance):
        pass


class SchemaInterface(object):
    @classmethod
    def validate_data(cls, data, instance=None):
        is_create = not(instance)
        pass

    @classmethod
    def retrieve_instance(cls, instance):
        pass

    @classmethod
    def retrieve_instances(cls, instances):
        pass


class User(Base):
    name = db.Colunt(db.String())
    age = db.Colunt(db.Integer())


class UserSchema(ma.Schema):
    name = ma.String()
    age = ma.Integer()


class BaseAPI(object):
    def get_queryset(self):
        raise NotImplementedError

    def pre_request(self):
        pass

    def post_request(self, response):
        pass

    def dispatch_request(self, method, *args, **kwargs):
        self.pre_request()
        response = method(*args, **kwargs)
        self.post_request(response)
        return response

    def list_(self):
        instances = ORMInterface.get_queryset(self.get_queryset())
        return jsonify(SchemaInterface.retrieve_instances(instances)), 200

    def create(self):
        normalized_request_data = FrameworkInterface.get_request_data(request)
        validated_data = SchemaInterface.validate_data(data)
        instance = ORMInterface.create_object(model, validated_data)
        return jsonify(SchemaInterface.retrieve_instance(instance)), 201

    def retrieve(self, pk):
        instance = ORMInterface.get_object(self.get_queryset(), pk)
        return jsonify(SchemaInterface.retrieve_instance(instance)), 200

    def update(self, pk):
        instance = ORMInterface.get_object(self.get_queryset(), pk)
        validated_data = SchemaInterface.validate_data(data, instance=instance)
        instance = ORMInterface.update_object(instance, validated_data)
        return jsonify(SchemaInterface.retrieve_instance(instance)), 200

    def delete(self, pk):
        instance = ORMInterface.get_object(self.get_queryset(), pk)
        ORMInterface.delete_object(instance)
        return jsonify(None), 204


class UserAPI(BaseAPI):
    model = User
    schema = UserSchema

    def get_queryset(self):
        return User.query


@route('/api/users/', methods=['GET'])
def list_():
    return UserApi.dispatch_request(UserAPI.list_)


@route('/api/users/', methods=['POST'])
def create():
    return UserApi.dispatch_request(UserAPI.create)


@route('/api/users/{pk}/', methods=['GET'])
def retrieve(pk):
    return UserApi.dispatch_request(UserAPI.retrieve, pk)


@route('/api/users/{pk}/', methods=['PATCH'])
def update(pk):
    return UserApi.dispatch_request(UserAPI.update, pk)


@route('/api/users/{pk}/', methods=['PATCH'])
def delete(pk):
    return UserApi.dispatch_request(UserAPI.delete, pk)
