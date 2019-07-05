from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    first_name = fields.String(required=True, validate=validate.Length(1))
    last_name = fields.String(required=True, validate=validate.Length(1))

    class Meta:
        dump_only = ('id', 'created')
        fields = dump_only + ('first_name', 'last_name')
