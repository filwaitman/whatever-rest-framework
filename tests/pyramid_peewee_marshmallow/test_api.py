import unittest

import mock
import pytest

from .api import MyBaseAPI
from .app import create_app, db
from .models import User


def _create_user(**data):
    user = User(**data)
    user.save()
    return user


class PyramidPeeweeMarshmallowTestCase(unittest.TestCase):
    def setUp(self):
        from webtest import TestApp  # Imported here in order to avoid dummy warning from pytest

        db.drop_tables([User])
        db.create_tables([User])

        self.app = create_app()
        self.client = TestApp(self.app)

    def test_list_users(self):
        _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/')
        assert response.status_code == 200
        assert response.json_body['count'] == 1
        assert response.json_body['next_page'] is None
        assert response.json_body['prev_page'] is None
        assert 'id' in response.json_body['results'][0]
        assert 'created' in response.json_body['results'][0]
        assert response.json_body['results'][0]['first_name'] == 'Filipe'
        assert response.json_body['results'][0]['last_name'] == 'Waitman'

    def test_create(self):
        data = {
            'first_name': 'Filipe',
            'last_name': 'Waitman',
        }

        response = self.client.post_json('/api/users/', data)
        assert response.status_code == 201
        assert response.json_body['first_name'] == 'Filipe'
        assert response.json_body['last_name'] == 'Waitman'
        assert response.json_body.get('id')
        assert response.json_body.get('created')
        assert User.select().filter(id=response.json_body['id']).count() == 1

        instance = User.select().filter(id=response.json_body['id']).get()
        assert instance.first_name == 'Filipe'
        assert instance.last_name == 'Waitman'

    def test_create_errors(self):
        data = {
            'first_name': 'Filipe',
            'last_name': 'Waitman',
        }

        response = self.client.post('/api/users/', data, status=400)
        assert response.status_code == 400
        assert response.json_body == {'first_name': ['Missing data for required field.'], 'last_name': ['Missing data for required field.'], 'status_code': 400}  # noqa

        del data['first_name']
        response = self.client.post_json('/api/users/', data, status=400)
        assert response.status_code == 400
        assert response.json_body == {'first_name': ['Missing data for required field.'], 'status_code': 400}

    def test_retrieve(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/{}/'.format(user.id))
        assert response.status_code == 200
        assert 'id' in response.json_body
        assert 'created' in response.json_body
        assert response.json_body['first_name'] == 'Filipe'
        assert response.json_body['last_name'] == 'Waitman'

    def test_retrieve_errors(self):
        response = self.client.get('/api/users/999/', status=404)
        assert response.status_code == 404
        assert response.json_body == {'status_code': 404}

    def test_update(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')
        data = {
            'last_name': 'New',
        }

        response = self.client.patch_json('/api/users/{}/'.format(user.id), data)
        assert response.status_code == 200
        assert 'id' in response.json_body
        assert 'created' in response.json_body
        assert response.json_body['first_name'] == 'Filipe'
        assert response.json_body['last_name'] == 'New'

        instance = User.select().filter(id=response.json_body['id']).get()
        assert instance.last_name == 'New'

    def test_update_errors(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')
        data = {
            'last_name': '',
        }

        response = self.client.patch_json('/api/users/{}/'.format(user.id), data, status=400)
        assert response.status_code == 400
        assert response.json_body == {'last_name': ['Shorter than minimum length 1.'], 'status_code': 400}

        instance = User.select().filter(id=user.id).get()
        assert instance.last_name == 'Waitman'

    def test_delete(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.delete('/api/users/{}/'.format(user.id))
        assert response.status_code == 204
        assert User.select().filter(id=user.id).count() == 0

    def test_doublename(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/{}/doublename/'.format(user.id))
        assert response.status_code == 200
        assert response.json_body == {'doubled': 'FilipeFilipe'}

    def test_pagination(self):
        _create_user(first_name='Filipe', last_name='Waitman')
        _create_user(first_name='John', last_name='Doe')

        response = self.client.get('/api/users/')
        assert response.status_code == 200
        assert response.json_body['count'] == 2
        assert response.json_body['next_page'] is None
        assert response.json_body['prev_page'] is None
        assert len(response.json_body['results']) == 2

        response = self.client.get('/api/users/?per_page=1&x=y')
        assert response.status_code == 200
        assert response.json_body['count'] == 2
        assert response.json_body['next_page'] is not None
        assert response.json_body['prev_page'] is None
        assert len(response.json_body['results']) == 1
        assert 'http' in response.json_body['next_page']
        assert 'localhost' in response.json_body['next_page']
        assert '/api/users/' in response.json_body['next_page']
        assert 'x=y' in response.json_body['next_page']
        assert 'per_page=1' in response.json_body['next_page']
        assert 'page=2' in response.json_body['next_page']

        response = self.client.get('/api/users/?per_page=1&page=2')
        assert response.status_code == 200
        assert response.json_body['count'] == 2
        assert response.json_body['next_page'] is None
        assert response.json_body['prev_page'] is not None
        assert len(response.json_body['results']) == 1

    @mock.patch.object(MyBaseAPI, 'get_current_user', return_value=None)
    def test_permissions(self, *mocks):
        user = _create_user(first_name='Filipe', last_name='Waitman')

        # User API
        response = self.client.get('/api/users/', status=401)
        assert response.status_code == 401

        response = self.client.post('/api/users/', status=401)
        assert response.status_code == 401

        response = self.client.get('/api/users/{}/'.format(user.id), status=401)
        assert response.status_code == 401

        response = self.client.patch('/api/users/{}/'.format(user.id), status=401)
        assert response.status_code == 401

        response = self.client.delete('/api/users/{}/'.format(user.id), status=401)
        assert response.status_code == 401

        response = self.client.get('/api/users/{}/doublename/'.format(user.id), status=401)
        assert response.status_code == 401

        # UserOpen API
        response = self.client.get('/api/users/{}/doublename_open/'.format(user.id))
        assert response.status_code == 200

        # UserReadOnly API
        response = self.client.get('/api/users/read_only/')
        assert response.status_code == 200

        response = self.client.post('/api/users/read_only/', status=403)
        assert response.status_code == 403

    def test_form_data_create(self):
        data = {
            'first_name': 'Filipe',
            'last_name': 'Waitman',
        }

        response = self.client.post_json('/api/users/form_data/', data, status=400)
        assert response.status_code == 400
        assert response.json_body == {'first_name': ['Missing data for required field.'], 'last_name': ['Missing data for required field.'], 'status_code': 400}  # noqa

        response = self.client.post('/api/users/form_data/', data)
        assert response.status_code == 201

    def test_no_pagination_list(self):
        _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/no_pagination/')
        assert response.status_code == 200
        assert len(response.json_body) == 1
        assert 'next_page' not in response.json_body
        assert 'prev_page' not in response.json_body
        assert 'id' in response.json_body[0]
        assert 'created' in response.json_body[0]
        assert response.json_body[0]['first_name'] == 'Filipe'
        assert response.json_body[0]['last_name'] == 'Waitman'

    def test_exception_behavior(self):
        response = self.client.get('/api/users/exception/handled/', status=499)
        assert response.status_code == 499
        assert response.json_body == {'detail': 'Now this is a weird HTTP code', 'status_code': 499}

        with pytest.raises(ZeroDivisionError):
            self.client.get('/api/users/exception/unhandled/')

        response = self.client.get('/api/users', status=404)  # Missing trailing slash (out of wrf scope)
        assert response.status_code == 404
