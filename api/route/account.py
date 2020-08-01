from flask import Blueprint
from api.schema.account import AccountSchema

account_api = Blueprint('account', __name__)


@account_api.route('/account', methods=['GET'])
def account():
    return AccountSchema().dump({}), 200
