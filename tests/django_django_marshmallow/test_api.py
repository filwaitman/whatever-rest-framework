import json
import os

import django
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_django_marshmallow.settings')
django.setup()

from django.contrib.auth.models import User as DjangoUser  # noqa  # isort:skip
from django.test import TestCase  # noqa  # isort:skip
from main.models import User  # noqa  # isort:skip


def _create_user(**data):
    return User.objects.create(**data)


def _as_json(payload):
    return {
        'data': json.dumps(payload),
        'content_type': 'application/json',
    }


class DjangoDjangoMarshmallowTestCase(TestCase):
    def setUp(self):
        super(DjangoDjangoMarshmallowTestCase, self).setUp()
        User.objects.all().delete()
        self.logged_in_user = DjangoUser.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        self.client.login(username='temporary', password='temporary')

    def test_list_users(self):
        _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/')
        assert response.status_code == 200

        response_json = response.json()
        assert response_json['count'] == 1
        assert response_json['next_page'] is None
        assert response_json['prev_page'] is None
        assert 'id' in response_json['results'][0]
        assert 'created' in response_json['results'][0]
        assert response_json['results'][0]['first_name'] == 'Filipe'
        assert response_json['results'][0]['last_name'] == 'Waitman'

    def test_create(self):
        data = {
            'first_name': 'Filipe',
            'last_name': 'Waitman',
        }

        response = self.client.post('/api/users/', **_as_json(data))
        assert response.status_code == 201

        response_json = response.json()
        assert response_json['first_name'] == 'Filipe'
        assert response_json['last_name'] == 'Waitman'
        assert response_json.get('id')
        assert response_json.get('created')
        assert User.objects.filter(id=response_json['id']).count() == 1

        instance = User.objects.filter(id=response_json['id']).get()
        assert instance.first_name == 'Filipe'
        assert instance.last_name == 'Waitman'

    def test_create_errors(self):
        data = {
            'first_name': 'Filipe',
            'last_name': 'Waitman',
        }

        response = self.client.post('/api/users/', data)
        assert response.status_code == 400
        assert response.json() == {'first_name': ['Missing data for required field.'], 'last_name': ['Missing data for required field.'], 'status_code': 400}  # noqa

        del data['first_name']
        response = self.client.post('/api/users/', **_as_json(data))
        assert response.status_code == 400
        assert response.json() == {'first_name': ['Missing data for required field.'], 'status_code': 400}

    def test_retrieve(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/{}/'.format(user.id))
        assert response.status_code == 200

        response_json = response.json()
        assert 'id' in response_json
        assert 'created' in response_json
        assert response_json['first_name'] == 'Filipe'
        assert response_json['last_name'] == 'Waitman'

    def test_retrieve_errors(self):
        response = self.client.get('/api/users/999/')
        assert response.status_code == 404
        assert response.json() == {'status_code': 404}

    def test_update(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')
        data = {
            'last_name': 'New',
        }

        response = self.client.patch('/api/users/{}/'.format(user.id), **_as_json(data))
        assert response.status_code == 200

        response_json = response.json()
        assert 'id' in response_json
        assert 'created' in response_json
        assert response_json['first_name'] == 'Filipe'
        assert response_json['last_name'] == 'New'

        instance = User.objects.filter(id=response_json['id']).get()
        assert instance.last_name == 'New'

    def test_update_errors(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')
        data = {
            'last_name': '',
        }

        response = self.client.patch('/api/users/{}/'.format(user.id), **_as_json(data))
        assert response.status_code == 400
        assert response.json() == {'last_name': ['Shorter than minimum length 1.'], 'status_code': 400}

        instance = User.objects.filter(id=user.id).get()
        assert instance.last_name == 'Waitman'

    def test_delete(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.delete('/api/users/{}/'.format(user.id))
        assert response.status_code == 204
        assert User.objects.filter(id=user.id).count() == 0

    def test_doublename(self):
        user = _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/{}/doublename/'.format(user.id))
        assert response.status_code == 200
        assert response.json() == {'doubled': 'FilipeFilipe'}
        assert response['header-passed-in'] == '1'

    def test_pagination(self):
        _create_user(first_name='Filipe', last_name='Waitman')
        _create_user(first_name='John', last_name='Doe')

        response = self.client.get('/api/users/')
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['count'] == 2
        assert response_json['next_page'] is None
        assert response_json['prev_page'] is None
        assert len(response_json['results']) == 2

        response = self.client.get('/api/users/?per_page=1&x=y')
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['count'] == 2
        assert response_json['next_page'] is not None
        assert response_json['prev_page'] is None
        assert len(response_json['results']) == 1
        assert 'http' in response_json['next_page']
        assert 'testserver' in response_json['next_page']
        assert '/api/users/' in response_json['next_page']
        assert 'x=y' in response_json['next_page']
        assert 'per_page=1' in response_json['next_page']
        assert 'page=2' in response_json['next_page']

        response = self.client.get('/api/users/?per_page=1&page=2')
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['count'] == 2
        assert response_json['next_page'] is None
        assert response_json['prev_page'] is not None
        assert len(response_json['results']) == 1

    def test_permissions(self, *mocks):
        self.client.logout()
        user = _create_user(first_name='Filipe', last_name='Waitman')

        # User API
        response = self.client.get('/api/users/')
        assert response.status_code == 401

        response = self.client.post('/api/users/')
        assert response.status_code == 401

        response = self.client.get('/api/users/{}/'.format(user.id))
        assert response.status_code == 401

        response = self.client.patch('/api/users/{}/'.format(user.id))
        assert response.status_code == 401

        response = self.client.delete('/api/users/{}/'.format(user.id))
        assert response.status_code == 401

        response = self.client.get('/api/users/{}/doublename/'.format(user.id))
        assert response.status_code == 401

        # UserOpen API
        response = self.client.get('/api/users/{}/doublename_open/'.format(user.id))
        assert response.status_code == 200

        # UserReadOnly API
        response = self.client.get('/api/users/read_only/')
        assert response.status_code == 200

        response = self.client.post('/api/users/read_only/')
        assert response.status_code == 403

    def test_form_data_create(self):
        data = {
            'first_name': 'Filipe',
            'last_name': 'Waitman',
        }

        response = self.client.post('/api/users/form_data/', **_as_json(data))
        assert response.status_code == 400

        response = self.client.post('/api/users/form_data/', data)
        assert response.status_code == 201

    def test_no_pagination_list(self):
        _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/no_pagination/')
        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == 1
        assert 'next_page' not in response_json
        assert 'prev_page' not in response_json
        assert 'id' in response_json[0]
        assert 'created' in response_json[0]
        assert response_json[0]['first_name'] == 'Filipe'
        assert response_json[0]['last_name'] == 'Waitman'

    def test_no_pagination_list_via_query_params(self):
        _create_user(first_name='Filipe', last_name='Waitman')

        response = self.client.get('/api/users/?paginate=f')
        assert response.status_code == 200
        response_json = response.json()
        assert len(response_json) == 1
        assert 'next_page' not in response_json
        assert 'prev_page' not in response_json
        assert 'id' in response_json[0]
        assert 'created' in response_json[0]
        assert response_json[0]['first_name'] == 'Filipe'
        assert response_json[0]['last_name'] == 'Waitman'

    def test_exception_behavior(self):
        response = self.client.get('/api/users/exception_handled/')
        assert response.status_code == 499
        assert response.json() == {'detail': 'Now this is a weird HTTP code', 'status_code': 499}

        with pytest.raises(ZeroDivisionError):
            self.client.get('/api/users/exception_unhandled/')

        response = self.client.get('/api/users')  # Missing trailing slash (out of wrf scope)
        assert response.status_code == 301
