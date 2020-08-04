import json

from flask import Response


class Reply(Response):
    def __init__(self, data: dict, msg=''):
        result = json.dumps(dict(code=200, msg=msg, data=data))
        Response.__init__(self, result, mimetype='application/json')


class ListReply(Response):
    def __init__(self, data: list, count: int, msg=''):
        result = json.dumps(dict(code=200, msg=msg, data=data, count=count))
        Response.__init__(self, result, mimetype='application/json')
