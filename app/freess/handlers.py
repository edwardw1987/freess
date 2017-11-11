# -*- coding: utf-8 -*-
# @Author: edward
# @Date:   2016-12-03 19:46:16
# @Last Modified by:   edward
# @Last Modified time: 2017-05-13 23:11:48

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from core import run_cmd_by_port, PORTS
from resource import iterShadowsocksResources
from tornado.gen import coroutine
import json

class FreeSS(RequestHandler):
    def get(self):
        self.render("freess.html")


class ApiServerList(RequestHandler):
    def get(self):
        server_gen = iterShadowsocksResources()
        server_list = list(server_gen)
        ret = {
            "server_list": [s['result'] for s in server_list],
            "ports": PORTS,
            "url": server_list[0]['url'] if server_list else 'n/a'

        }
        self.set_header('content-type', 'application/json')
        self.write(json.dumps(ret))

class FreeSSLocalServer(RequestHandler):
    def get(self):
        port = self.get_argument('port')
        cmd = self.get_argument('cmd')
        if 0 == run_cmd_by_port(cmd, port):
            self.write('ok')
        else:
            self.write('fail')


class FreeSSWebSocket(WebSocketHandler):
    resource_gen = None
    index = 1

    def open(self):
        if self.resource_gen is None:
            self.resource_gen = iterShadowsocksResources()

    def on_message(self, message):
        next_resource = next(self.resource_gen, None)
        if not next_resource:
            self.resource_gen = None
            self.index = 1
            return self.write_message('over')
        msg = self.render_string("freess_row.html",
                                 ports=PORTS,
                                 index=self.index,
                                 resource=next_resource,
                                 )
        self.write_message(msg)
        self.index += 1

    def on_close(self):
        print("WebSocket closed")

from tornado.ioloop import IOLoop
import logging

LOG = logging.getLogger(__name__)

class MainHandler(RequestHandler):
    @coroutine
    def get(self):
        tsk = task.Freevpnss(IOLoop.current())
        yield tsk.start() # callback, not return
        for fn, arg in tsk.iter_jobs():
            # arg["country"] = get_country_by_addr(arg["addr"])
            LOG.info('============>>>%s' % fn(arg) )

handlers = [
    ('/main/?', MainHandler),
    ('/freess.html', FreeSS),
    ('/freess/localserver/run/', FreeSSLocalServer, None, 'freess.run'),
    ('/freess/ws/', FreeSSWebSocket, None, 'freess.ws'),
    ('/freess/api/server/?', ApiServerList, None, 'freess.api.serverlist')
]
