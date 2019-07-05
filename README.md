# Whatever REST Framework

## DISCLAIMER:

This is WIP. Next steps I can think:
- Add support to framework=tornado
- Add support to framework=Django
- Add support to ORM=Django
- Review the TODOs I have left in the project 
- Create a better documentation (and document the base components)
- Allow custom headers in responses


## What?

Basically this is an agnostic and thin layer to create RESTful APIs.


## Why?

Honestly because I every time I have to develop an API I tend to use Django just because of Django Rest Framework (and yes, this is my personal opinion).  
I would love to be able to create my RESTful APIs in whatever framework/technology I wanted to.


## How?

There are a bunch of full working projects as examples. Please see the [tests folder]().  
In short: you basically need to define the components you want to use (I suggest doing this in a base API class). For instance, below is all you need to get a simple flask API:

```python
from functools import partial

from wrf.api.base import BaseAPI
from wrf.framework.flask import FlaskFrameworkComponent
from wrf.orm.sqlalchemy import SQLAlchemyORMComponent
from wrf.schema.marshmallow_sqlalchemy import MarshmallowSQLAlchemySchemaComponent

from <your_stuff> import app, db, User, UserSchema

class MyBaseAPI(BaseAPI):
    ORM_COMPONENT = partial(SQLAlchemyORMComponent, db=db)
    SCHEMA_COMPONENT = MarshmallowSQLAlchemySchemaComponent
    FRAMEWORK_COMPONENT = FlaskFrameworkComponent

    def get_current_user(self):
        return {'name': 'Filipe'}

class UserAPI(MyBaseAPI):
    model_class = User
    schema_class = UserSchema

    def get_queryset(self):
        return User.query

@app.route('/', methods=['GET'])
def list_():
    api = UserAPI(request)
    return api.dispatch_request(api.list_)

@app.route('/', methods=['POST'])
def create():
    api = UserAPI(request)
    return api.dispatch_request(api.create)

@app.route('/<int:pk>/', methods=['GET'])
def retrieve(pk):
    api = UserAPI(request)
    return api.dispatch_request(api.retrieve, pk)

@app.route('/<int:pk>/', methods=['PATCH'])
def update(pk):
    api = UserAPI(request)
    return api.dispatch_request(api.update, pk)

@app.route('/<int:pk>/', methods=['DELETE'])
def delete(pk):
    api = UserAPI(request)
    return api.dispatch_request(api.delete, pk)
```


## Supported technologies

### Framework:
- Chalice
- Flask
- Pyramid


### ORM:
- Peewee
- SQLAlchemy


### Schema:
- Marshmallow
- Marshmallow-SQLAlchemy

Bear in mind that this project is made to be easily extensible, so if you need to connect something else, it's simple to do it.


## Contributing

Please [open issues]() if you see one, or [create a pull request]() when possible.  
In case of a pull request, please consider the following:
- Respect the line length is 132 characters
- Keep the great test coverage of this project
- Run `tox` locally so you can see if everything is green (including linter and other python versions)
