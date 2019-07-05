from marshmallow import fields, validate
from marshmallow_sqlalchemy import ModelSchema

from .app import db
from .models import User


class UserSchema(ModelSchema):
    first_name = fields.String(required=True, validate=validate.Length(1))
    last_name = fields.String(required=True, validate=validate.Length(1))

    class Meta:
        model = User
        sqla_session = db.session
        dump_only = ('id', 'created')
        fields = dump_only + ('first_name', 'last_name')
