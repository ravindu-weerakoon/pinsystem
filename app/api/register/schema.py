from marshmallow import Schema, fields, validate


class RegistrationSchema(Schema):
    email = fields.Email(required=True)
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=8))
    fullname = fields.Str(required=True, validate=validate.Length(min=1))
