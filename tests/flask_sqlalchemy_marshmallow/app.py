from flask import Flask
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
ma = Marshmallow()


def create_app(script_info=None):
    app = Flask(__name__)
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })

    db.init_app(app)
    ma.init_app(app)

    from .api import users_api_bp
    app.register_blueprint(users_api_bp, url_prefix='/api/users')

    app.before_request(lambda: db.create_all())

    return app
