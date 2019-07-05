from flask import Flask
from flask_marshmallow import Marshmallow
from peewee import SqliteDatabase

db = SqliteDatabase(':memory:')
ma = Marshmallow()


def create_app(script_info=None):
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
    })

    ma.init_app(app)

    from .api import users_api_bp
    from .models import User
    app.register_blueprint(users_api_bp, url_prefix='/api/users')

    app.before_request(lambda: db.create_tables([User]))

    return app
