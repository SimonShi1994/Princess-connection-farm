from typing import Optional

from flask import Flask, render_template, request
from flask_cors import CORS
from flasgger import Swagger
from api.route.account import account_api
from api.route.schedule import schedule_api
from api.route.batch import batches_api
from api.route.clan import clan_api
from api.route.task import task_api
from api.route.subtask import subtask_api
from api.route.ocr import ocr_api
from utils import STATIC_PATH, DIST_PATH
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def create_app():
    app = Flask(__name__, static_folder=STATIC_PATH, template_folder=DIST_PATH)
    app.url_map.converters['reg'] = RegexConverter

    CORS(app, supports_credentials=True)

    @app.route('/', defaults={'path': ''})
    @app.route('/<reg("((?!(api|apidocs|ocr|demo)).)+"):path>')  # 暂 api|apidoc|ocr|demo 以外的所有路由视为前端路由
    def index(path):
        return render_template("index.html")

    app.register_blueprint(account_api, url_prefix='/api')
    app.register_blueprint(schedule_api, url_prefix='/api')
    app.register_blueprint(clan_api, url_prefix='/api')
    app.register_blueprint(task_api, url_prefix='/api')
    app.register_blueprint(subtask_api, url_prefix='/api')
    app.register_blueprint(batches_api, url_prefix='/api')
    app.register_blueprint(ocr_api, url_prefix='/ocr')

    # `task_func` is PyWebIO task function
    from pywebio.platform.flask import webio_view
    import main_webUI

    app.add_url_rule('/demo', 'webio_view', webio_view(main_webUI.emuidemo),
                     methods=['GET', 'POST', 'OPTIONS'])  # need GET,POST and OPTIONS methods

    # http://127.0.0.1:5000/demo

    # app.register_blueprint(emulator_api, url_prefix='/api')

    app.config['SWAGGER'] = {
        'title': 'Princess Connection Farm',
    }
    Swagger(app)
    return app


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    parser.add_argument('-d', '--debug', default=True, type=bool)
    args = parser.parse_args()

    app = create_app()
    app.run(host='127.0.0.1', port=args.port, debug=False)
