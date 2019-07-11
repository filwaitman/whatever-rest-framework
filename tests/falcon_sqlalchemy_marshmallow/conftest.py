import pytest
from falcon import testing

from tests.falcon_sqlalchemy_marshmallow.app import create_app


@pytest.fixture
def client():
    return testing.TestClient(create_app())
