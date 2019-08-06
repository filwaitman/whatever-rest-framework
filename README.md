[![Build Status](https://travis-ci.org/filwaitman/whatever-rest-framework.svg?branch=master)](https://travis-ci.org/filwaitman/whatever-rest-framework)
[![codecov](https://codecov.io/gh/filwaitman/whatever-rest-framework/branch/master/graph/badge.svg)](https://codecov.io/gh/filwaitman/whatever-rest-framework)

# Whatever REST Framework

## DISCLAIMER:

This is WIP. Next steps I can think:
- Review the TODOs I have left in the project 
- Document input/output of every component's method
- Create unit tests for base components


## What?

Basically this is an agnostic and thin layer to create RESTful APIs.


## Why?

Honestly because I every time I have to develop an API I tend to use Django just because of Django Rest Framework (and yes, this is my personal opinion).  
I would love to be able to create my RESTful APIs in whatever framework/technology I wanted to.


## How?

`pip install whatever-rest-framework`

There are a bunch of full working projects as examples. Please see the [tests folder](https://github.com/filwaitman/whatever-rest-framework/tree/master/tests).  

In details, you'll need to:  

### 1) Create an `APIOrchestrator` by choosing a bunch of components

The types of base components you can choose for the API orchestrator are:

| Type                       | Implementations                                                                                                                    | Must be set? | Default                     |
|----------------------------|------------------------------------------------------------------------------------------------------------------------------------|--------------|-----------------------------|
| framework_component_class  | ChaliceFrameworkComponent, DjangoFrameworkComponent, FalconFrameworkComponent, FlaskFrameworkComponent, PyramidFrameworkComponent  | Yes          | None                        |
| orm_component_class        | DjangoORMComponent, PeeweeORMComponent, SQLAlchemyORMComponent                                                                     | Yes          | None                        |
| schema_component_class     | MarshmallowSchemaComponent, MarshmallowSQLAlchemySchemaComponent                                                                   | Yes          | None                        |
| error_component_class      | DefaultErrorComponent                                                                                                              | No           | DefaultErrorComponent       |
| pagination_component_class | NoPagePaginationComponent, PagePagePaginationComponent                                                                             | No           | NoPagePaginationComponent   |
| permission_component_class | AllowAllPermissionComponent, AllowAuthenticatedPermissionComponent, ReadOnlyPermissionComponent                                    | No           | AllowAllPermissionComponent |

### 2) Define the `get_current_user(self)` method inside this orchestrator

The logic to discover the current user of a request is heavily dependant of the framework (and the tools you use), and I decided not to include it in the scope of this project.
Ideally this can be simple as `def get_current_user(self): return g.user` or even `def get_current_user(self): return self.request.user if self.request.user.is_authenticated else None`.

### 3) Create your APIs inheriting from the `APIOrchestrator`

These APIs need to set the attributes `model_class` and `schema_class`. Also you have to set the `get_queryset(self)`method.
Here you have full, magic access to the basic API CRUD methods (list resources, retrieve resource, create resource, update resource, delete resource).  

**Special note: the `@api_view()` decorator:**

You can add other specific methods to your needs by adding methods to the API class too! Just decorate your custom methods with the `@api_view()` decorator and you're good to go!
This decorator can receive as arguments the components override to be used for that particular method. So you can have, for instance, your APIOrchestrator with permission=`AllowAllPermissionComponent` but this particular method with permission=`AllowAuthenticatedPermissionComponent` just by like below:

```python
class APIOrchestrator(BaseAPI):
    permission_component_class = AllowAllPermissionComponent
    # ...

    @api_view(permission_component_class=AllowAuthenticatedPermissionComponent)
    def retrieve_more_private_stuff(self):
        return {'super-private': 'data'}
```

### Working example for a flask application:

```python
from functools import partial

from wrf.api.base import BaseAPI, api_view
from wrf.framework.flask import FlaskFrameworkComponent
from wrf.orm.sqlalchemy import SQLAlchemyORMComponent
from wrf.schema.marshmallow_sqlalchemy import MarshmallowSQLAlchemySchemaComponent

from <your_stuff> import app, db, User, UserSchema

class APIOrchestrator(BaseAPI):
    orm_component_class = partial(SQLAlchemyORMComponent, session=db.session)
    schema_component_class = MarshmallowSQLAlchemySchemaComponent
    framework_component_class = FlaskFrameworkComponent

    def get_current_user(self):
        # from flask_login import current_user; return current_user # if you're using flask-login, for example
        # return self.request.user if self.request.user.is_authenticated else None  # if you're using django, for example
        return {'name': 'Filipe'}

class UserAPI(APIOrchestrator):
    model_class = User
    schema_class = UserSchema

    def get_queryset(self):
        return User.query
    
    @api_view()
    def retrieve_something_else(self, pk):
        user = User.query.filter_by(id=pk).one()
        return {'something_else': user.something_else}

@app.route('/', methods=['GET'])
def list_():
    return UserAPI(request).list()

@app.route('/', methods=['POST'])
def create():
    return UserAPI(request).create()

@app.route('/<int:pk>/', methods=['GET'])
def retrieve(pk):
    return UserAPI(request).retrieve(pk)

@app.route('/<int:pk>/', methods=['PATCH'])
def update(pk):
    return UserAPI(request).update(pk)

@app.route('/<int:pk>/', methods=['DELETE'])
def delete(pk):
    return UserAPI(request).delete(pk)

@app.route('/<int:pk>/something_else/', methods=['GET'])
def retrieve_something_else(pk):
    return UserAPI(request).retrieve_something_else(pk)
```


## Supported technologies

### Framework:
- Chalice
- Django
- Falcon
- Flask
- Pyramid


### ORM:
- Django
- Peewee
- SQLAlchemy


### Schema:
- Marshmallow
- Marshmallow-SQLAlchemy

Bear in mind that this project is made to be easily extensible, so if you need to connect something else, it's simple to do it. [Check how simple it is to add support to a new framework](https://github.com/filwaitman/whatever-rest-framework/tree/master/wrf/framework/flask.py), for example. =D


## Contributing

Please [open issues](https://github.com/filwaitman/whatever-rest-framework/issues) if you see one, or [create a pull request](https://github.com/filwaitman/whatever-rest-framework/pulls) when possible.  
In case of a pull request, please consider the following:
- Respect the line length (132 characters)
- Keep the great test coverage of this project
- Run `tox` locally so you can see if everything is green (including linter and other python versions)
