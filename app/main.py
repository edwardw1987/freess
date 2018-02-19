#!/usr/bin/env python
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.options import options, define
from lib.mylogger import init_logger
from lib.tornado_utils import Application, JinjaLoader

import os
import freess

init_logger(__file__, "freess.log")

def main():
    define('port', default=8000, help="run on the port", type=int)
    define('debug', default=False, help='run in debug mode', type=bool)
    options.parse_command_line()
    curdir = os.path.dirname(__file__)
    settings = dict(
        template_loader=JinjaLoader(os.path.join(curdir, 'template')),
        static_path=os.path.join(curdir, 'static'),
        # cookie_secret="d5b0df6d65704feda3e7f79ba9b5f677",
        # login_url='/login',
        # xsrf_cookies=False,
        debug=options.debug,
        gzip=False,
    )
    app = Application(**settings)
    app.add_handlers_with_prefix(".*", freess.handlers, '/spa')
    server = HTTPServer(app)
    server.listen(options.port)
    IOLoop.current().start()


if __name__ == "__main__":
    main()
