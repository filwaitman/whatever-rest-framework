import json

import pytest

from .api import MyBaseAPI
from .app import Base, User, engine, session


@pytest.fixture(autouse=True)
def _setup():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def _create_user(**data):
    user = User(**data)
    session.add(user)
    session.flush()
    session.commit()
    return user


def _as_json(payload):
    return {
        'body': json.dumps(payload),
    }


def test_list_users(client):
    _create_user(first_name='Filipe', last_name='Waitman')

    response = client.simulate_get('/api/users')
    assert response.status_code == 200
    assert response.json['count'] == 1
    assert response.json['next_page'] is None
    assert response.json['prev_page'] is None
    assert 'id' in response.json['results'][0]
    assert 'created' in response.json['results'][0]
    assert response.json['results'][0]['first_name'] == 'Filipe'
    assert response.json['results'][0]['last_name'] == 'Waitman'


def test_create(client):
    data = {
        'first_name': 'Filipe',
        'last_name': 'Waitman',
    }

    response = client.simulate_post('/api/users', **_as_json(data))
    assert response.status_code == 201
    assert response.json['first_name'] == 'Filipe'
    assert response.json['last_name'] == 'Waitman'
    assert response.json.get('id')
    assert response.json.get('created')
    assert session.query(User).filter_by(id=response.json['id']).count() == 1

    instance = session.query(User).get(response.json['id'])
    assert instance.first_name == 'Filipe'
    assert instance.last_name == 'Waitman'


def test_create_errors(client):
    data = {
        'last_name': 'Waitman',
    }

    response = client.simulate_post('/api/users', **_as_json(data))
    assert response.status_code == 400
    assert response.json == {'first_name': ['Missing data for required field.'], 'status_code': 400}


def test_retrieve(client):
    user = _create_user(first_name='Filipe', last_name='Waitman')

    response = client.simulate_get('/api/users/{}'.format(user.id))
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'created' in response.json
    assert response.json['first_name'] == 'Filipe'
    assert response.json['last_name'] == 'Waitman'


def test_retrieve_errors(client):
    response = client.simulate_get('/api/users/999')
    assert response.status_code == 404
    assert response.json == {'status_code': 404}


def test_update(client):
    user = _create_user(first_name='Filipe', last_name='Waitman')
    data = {
        'last_name': 'New',
    }

    response = client.simulate_patch('/api/users/{}'.format(user.id), **_as_json(data))
    assert response.status_code == 200
    assert 'id' in response.json
    assert 'created' in response.json
    assert response.json['first_name'] == 'Filipe'
    assert response.json['last_name'] == 'New'

    instance = session.query(User).get(response.json['id'])
    assert instance.last_name == 'New'


def test_update_errors(client):
    user = _create_user(first_name='Filipe', last_name='Waitman')
    data = {
        'last_name': '',
    }

    response = client.simulate_patch('/api/users/{}'.format(user.id), **_as_json(data))
    assert response.status_code == 400
    assert response.json == {'last_name': ['Shorter than minimum length 1.'], 'status_code': 400}

    instance = session.query(User).get(user.id)
    assert instance.last_name == 'Waitman'


def test_delete(client):
    user = _create_user(first_name='Filipe', last_name='Waitman')

    response = client.simulate_delete('/api/users/{}'.format(user.id))
    assert response.status_code == 204
    assert session.query(User).filter_by(id=user.id).count() == 0


def test_doublename(client):
    user = _create_user(first_name='Filipe', last_name='Waitman')

    response = client.simulate_get('/api/users/{}/doublename'.format(user.id))
    assert response.status_code == 200
    assert response.json == {'doubled': 'FilipeFilipe'}
    assert response.headers['header-passed-in'] == '1'


def test_pagination(client):
    _create_user(first_name='Filipe', last_name='Waitman')
    _create_user(first_name='John', last_name='Doe')

    response = client.simulate_get('/api/users')
    assert response.status_code == 200
    assert response.json['count'] == 2
    assert response.json['next_page'] is None
    assert response.json['prev_page'] is None
    assert len(response.json['results']) == 2

    response = client.simulate_get('/api/users?per_page=1&x=y')
    assert response.status_code == 200
    assert response.json['count'] == 2
    assert response.json['next_page'] is not None
    assert response.json['prev_page'] is None
    assert len(response.json['results']) == 1
    assert 'http' in response.json['next_page']
    assert 'falconframework.org' in response.json['next_page']
    assert '/api/users' in response.json['next_page']
    assert 'x=y' in response.json['next_page']
    assert 'per_page=1' in response.json['next_page']
    assert 'page=2' in response.json['next_page']

    response = client.simulate_get('/api/users?per_page=1&page=2')
    assert response.status_code == 200
    assert response.json['count'] == 2
    assert response.json['next_page'] is None
    assert response.json['prev_page'] is not None
    assert len(response.json['results']) == 1


def test_permissions(client, mocker):
    mocker.patch.object(MyBaseAPI, 'get_current_user', return_value=None)
    user = _create_user(first_name='Filipe', last_name='Waitman')

    # User API
    response = client.simulate_get('/api/users')
    assert response.status_code == 401

    response = client.simulate_post('/api/users')
    assert response.status_code == 401

    response = client.simulate_get('/api/users/{}'.format(user.id))
    assert response.status_code == 401

    response = client.simulate_patch('/api/users/{}'.format(user.id))
    assert response.status_code == 401

    response = client.simulate_delete('/api/users/{}'.format(user.id))
    assert response.status_code == 401

    response = client.simulate_get('/api/users/{}/doublename'.format(user.id))
    assert response.status_code == 401

    # UserOpen API
    response = client.simulate_get('/api/users/{}/doublename_open'.format(user.id))
    assert response.status_code == 200

    # UserReadOnly API
    response = client.simulate_get('/api/users/read_only')
    assert response.status_code == 200

    response = client.simulate_post('/api/users/read_only')
    assert response.status_code == 403


def test_no_pagination_list(client):
    _create_user(first_name='Filipe', last_name='Waitman')

    response = client.simulate_get('/api/users/no_pagination')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert 'next_page' not in response.json
    assert 'prev_page' not in response.json
    assert 'id' in response.json[0]
    assert 'created' in response.json[0]
    assert response.json[0]['first_name'] == 'Filipe'
    assert response.json[0]['last_name'] == 'Waitman'


def test_no_pagination_list_via_query_params(client):
    _create_user(first_name='Filipe', last_name='Waitman')

    response = client.simulate_get('/api/users?paginate=f')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert 'next_page' not in response.json
    assert 'prev_page' not in response.json
    assert 'id' in response.json[0]
    assert 'created' in response.json[0]
    assert response.json[0]['first_name'] == 'Filipe'
    assert response.json[0]['last_name'] == 'Waitman'


def test_exception_behavior(client):
    response = client.simulate_get('/api/users/exception/handled')
    assert response.status_code == 451
    assert response.json == {'detail': 'Now this is a weird HTTP code', 'status_code': 451}

    with pytest.raises(ZeroDivisionError):
        client.simulate_get('/api/users/exception/unhandled')

    # Framework-specific error (not handled/touched by wrf)
    response = client.simulate_get('/api/')
    assert response.status_code == 404
    assert response.json is None
