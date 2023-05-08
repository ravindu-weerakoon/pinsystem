from marshmallow import Schema, fields, validate


class PinSchema(Schema):

    title = fields.Str(required=True, validate=validate.Length(min=1))
    body = fields.Str(required=True, validate=validate.Length(min=1))
    image = fields.Str(required=False, validate=validate.Length(min=3))
    date_posted = fields.DateTime(required=False)
    updated_date = fields.DateTime(required=False)


class UpdatePinsSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=1))
    body = fields.Str(required=False, validate=validate.Length(min=1))
    image = fields.Str(required=False, validate=validate.Length(min=3))
    updated_date = fields.DateTime(required=False)
