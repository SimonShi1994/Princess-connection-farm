from flask_marshmallow import Schema
from marshmallow import fields


class AccountSchema(Schema):
    class Meta:
        fields = ["username", "password"]

    username = fields.String()
    password = fields.String()
