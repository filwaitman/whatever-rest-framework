from wsgiref.simple_server import make_server

from peewee import SqliteDatabase
from pyramid.config import Configurator
from pyramid.events import NewRequest

db = SqliteDatabase(':memory:')


def create_app():
    from tests.pyramid_peewee_marshmallow.models import User

    with Configurator() as config:
        config.add_route('users_list', '/api/users/', request_method=['GET'])
        config.add_route('users_create', '/api/users/', request_method=['POST'])
        config.add_route('users_read_only_list_and_create', '/api/users/read_only/', request_method=['GET', 'POST'])
        config.add_route('users_form_data_create', '/api/users/form_data/', request_method=['POST'])
        config.add_route('users_no_pagination_list', '/api/users/no_pagination/', request_method=['GET'])
        config.add_route('users_handled_exception_list', '/api/users/exception/handled/', request_method=['GET'])
        config.add_route('users_unhandled_exception_list', '/api/users/exception/unhandled/', request_method=['GET'])
        config.add_route('users_retrieve', '/api/users/{pk}/', request_method=['GET'])
        config.add_route('users_update', '/api/users/{pk}/', request_method=['PATCH'])
        config.add_route('users_delete', '/api/users/{pk}/', request_method=['DELETE'])
        config.add_route('users_doublename', '/api/users/{pk}/doublename/', request_method=['GET'])
        config.add_route('users_open_doublename', '/api/users/{pk}/doublename_open/', request_method=['GET'])

        config.add_subscriber(lambda event: db.create_tables([User]), NewRequest)
        config.scan('tests.pyramid_peewee_marshmallow.api')
        app = config.make_wsgi_app()

    return app


if __name__ == '__main__':
    app = create_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()
