#!/usr/bin/env python
from flask import Flask
import freess
from lib import util
from lib.mylogger import init_logger


def make_app(debug=False, **kwargs):
    app = Flask(__name__)
    app.jinja_env.auto_reload = True
    app.jinja_env.globals.update(**kwargs)
    return app

init_logger(__file__, "freess.log")
app = make_app()
app.register_blueprint(freess.app, url_prefix="/spa")
util.init_app(app)
