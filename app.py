import os

from flask import Flask, render_template
from api.route.account import account_api
from utils import STATIC_PATH, DIST_PATH
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def create_app():
    app = Flask(__name__, static_folder=STATIC_PATH, template_folder=DIST_PATH)
    app.url_map.converters['reg'] = RegexConverter

    @app.route('/', defaults={'path': ''})
    @app.route('/<reg("((?!api).)+"):path>')  # 暂 api 以外的所有路由视为前端路由
    def index(path):
        return render_template("index.html")

    app.register_blueprint(account_api, url_prefix='/api')

    return app


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-d', '--debug', default=True, type=bool)
    args = parser.parse_args()

    app = create_app()
    app.run(host='127.0.0.1', port=args.port, debug=args.debug)
