import os

from flask import Flask

from analyzer.dburi import DbURI


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=DbURI.conn_string,
    )

    if not test_config:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return '<h1>Oi, mates!</h1>'

    from . import postgres_db
    postgres_db.init_app(app)

    from .bps import lotto, multi
    app.register_blueprint(lotto.bp)
    app.register_blueprint(multi.bp)

    return app
