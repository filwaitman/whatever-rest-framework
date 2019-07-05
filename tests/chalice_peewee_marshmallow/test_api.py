import json
from collections import namedtuple

import pytest

from .app import MyBaseAPI, User, app, db


@pytest.fixture(autouse=True)
def _setup():
    db.drop_tables([User])
    db.create_tables([User])


def _create_user(**data):
    user = User(**data)
    user.save()
    return user


def _as_json(payload):
    return {
        'data': json.dumps(payload),
        'content_type': 'application/json',
    }


def create_event(method, uri, data=None, path_parameters=None, query_params=None, content_type='application/json'):
    path_parameters = path_parameters or {}

    data = data or {}
    if data:
        data = json.dumps(data)

    query_params = query_params or {}
    query_params = {k: [v] for k, v in query_params.items()}

    return {
        'requestContext': {
            'httpMethod': method,
            'resourcePath': uri,
        },
        'headers': {
            'Content-Type': content_type,
        },
        'pathParameters': path_parameters,
        'multiValueQueryStringParameters': None,
        'body': data,
        'stageVariables': {},
        'multiValueQueryStringParameters': query_params,
    }


def _get_response(method, path, *args, **kwargs):
    event = create_event(method, path, *args, **kwargs)
    raw_response = app(event, context=None)
    Response = namedtuple('Response', ['status_code', 'json'])
    return Response(status_code=raw_response['statusCode'], json=json.loads(raw_response['body']))


def test_list_users():
    _create_user(first_name='Filipe', last_name='Waitman')

    response = _get_response('GET', '/api/users')
    assert response.status_code == 200
    assert response.json['count'] == 1
    assert response.json['next_page'] is None
    assert response.json['prev_page'] is None
    assert 'id' in response.json['results'][0]
    assert 'created' in response.json['results'][0]
    assert response.json['results'][0]['first_name'] == 'Filipe'
    assert response.json['results'][0]['last_name'] == 'Waitman'


def test_create():
    data = {
        'first_name': 'Filipe',
        'last_name': 'Waitman',
    }

    response = _get_response('POST', '/api/users', data=data)
    assert response.status_code == 201
    assert response.json['first_name'] == 'Filipe'
    assert response.json['last_name'] == 'Waitman'
    assert response.json.get('id')
    assert response.json.get('created')
    assert User.select().filter(id=response.json['id']).count() == 1

    instance = User.select().filter(id=response.json['id']).get()
    assert instance.first_name == 'Filipe'
    assert instance.last_name == 'Waitman'


def test_create_errors():
    data = {
        'last_name': 'Waitman',
    }

    response = _get_response('POST', '/api/users', data=data)
    assert response.status_code == 400
    assert response.json == {'first_name': ['Missing data for required field.'], 'status_code': 400}


def test_retrieve():
    user = _create_user(first_name='Filipe', last_name='Waitman')

    response = _get_response('GET', '/api/users/{pk}', path_parameters={'pk': user.id})
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'created' in response.json
    assert response.json['first_name'] == 'Filipe'
    assert response.json['last_name'] == 'Waitman'


def test_retrieve_errors():
    response = _get_response('GET', '/api/users/{pk}', path_parameters={'pk': '999'})
    assert response.status_code == 404
    assert response.json == {'status_code': 404}


def test_update():
    user = _create_user(first_name='Filipe', last_name='Waitman')
    data = {
        'last_name': 'New',
    }

    response = _get_response('PATCH', '/api/users/{pk}', data=data, path_parameters={'pk': user.id})
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'created' in response.json
    assert response.json['first_name'] == 'Filipe'
    assert response.json['last_name'] == 'New'

    instance = User.select().filter(id=response.json['id']).get()
    assert instance.last_name == 'New'


def test_update_errors():
    user = _create_user(first_name='Filipe', last_name='Waitman')
    data = {
        'last_name': '',
    }

    response = _get_response('PATCH', '/api/users/{pk}', data=data, path_parameters={'pk': user.id})
    assert response.status_code == 400
    assert response.json == {'last_name': ['Shorter than minimum length 1.'], 'status_code': 400}

    instance = User.select().filter(id=user.id).get()
    assert instance.last_name == 'Waitman'


def test_delete():
    user = _create_user(first_name='Filipe', last_name='Waitman')

    response = _get_response('DELETE', '/api/users/{pk}', path_parameters={'pk': user.id})
    assert response.status_code == 204
    assert User.select().filter(id=user.id).count() == 0


def test_doublename():
    user = _create_user(first_name='Filipe', last_name='Waitman')

    response = _get_response('GET', '/api/users/{pk}/doublename', path_parameters={'pk': user.id})
    assert response.status_code == 200
    assert response.json == {'doubled': 'FilipeFilipe'}


def test_pagination():
    _create_user(first_name='Filipe', last_name='Waitman')
    _create_user(first_name='John', last_name='Doe')

    response = _get_response('GET', '/api/users')
    assert response.status_code == 200
    assert response.json['count'] == 2
    assert response.json['next_page'] is None
    assert response.json['prev_page'] is None
    assert len(response.json['results']) == 2

    response = _get_response('GET', '/api/users', query_params={'per_page': '1', 'x': 'y'})
    assert response.status_code == 200
    assert response.json['count'] == 2
    assert response.json['next_page'] is not None
    assert response.json['prev_page'] is None
    assert len(response.json['results']) == 1
    # assert 'http' in response.json['next_page']  # TODO [later]
    # assert 'localhost' in response.json['next_page']  # TODO [later]
    assert '/api/users' in response.json['next_page']
    assert 'x=y' in response.json['next_page']
    assert 'per_page=1' in response.json['next_page']
    assert 'page=2' in response.json['next_page']

    response = _get_response('GET', '/api/users', query_params={'per_page': '1', 'page': '2'})
    assert response.status_code == 200
    assert response.json['count'] == 2
    assert response.json['next_page'] is None
    assert response.json['prev_page'] is not None
    assert len(response.json['results']) == 1


def test_permissions(mocker):
    mocker.patch.object(MyBaseAPI, 'get_current_user', return_value=None)
    user = _create_user(first_name='Filipe', last_name='Waitman')

    # User API
    response = _get_response('GET', '/api/users')
    assert response.status_code == 401

    response = _get_response('GET', '/api/users')
    assert response.status_code == 401

    response = _get_response('GET', '/api/users/{pk}', path_parameters={'pk': user.id})
    assert response.status_code == 401

    response = _get_response('GET', '/api/users/{pk}', path_parameters={'pk': user.id})
    assert response.status_code == 401

    response = _get_response('GET', '/api/users/{pk}', path_parameters={'pk': user.id})
    assert response.status_code == 401

    response = _get_response('GET', '/api/users/{pk}/doublename', path_parameters={'pk': user.id})
    assert response.status_code == 401

    # UserOpen API
    response = _get_response('GET', '/api/users/{pk}/doublename_open', path_parameters={'pk': user.id})
    assert response.status_code == 200

    # UserReadOnly API
    response = _get_response('GET', '/api/users/read_only')
    assert response.status_code == 200

    response = _get_response('POST', '/api/users/read_only')
    assert response.status_code == 403


def test_no_pagination_list():
    _create_user(first_name='Filipe', last_name='Waitman')

    response = _get_response('GET', '/api/users/no_pagination')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert 'next_page' not in response.json
    assert 'prev_page' not in response.json
    assert 'id' in response.json[0]
    assert 'created' in response.json[0]
    assert response.json[0]['first_name'] == 'Filipe'
    assert response.json[0]['last_name'] == 'Waitman'


def test_exception_behavior():
    response = _get_response('GET', '/api/users/exception/handled')
    assert response.status_code == 499
    assert response.json == {'detail': 'Now this is a weird HTTP code', 'status_code': 499}

    response = _get_response('GET', '/api/users/exception/unhandled')
    assert response.status_code == 500
