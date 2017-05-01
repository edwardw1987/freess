# -*- coding: utf-8 -*-
# @Author: edward
# @Date:   2016-12-03 19:46:16
# @Last Modified by:   edward
# @Last Modified time: 2016-12-18 00:13:06

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler

from core import run_cmd_by_port, PORTS
from resource import iterShadowsocksResources


class FreeSS(RequestHandler):
    def get(self):
        self.render("freess.html")


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


handlers = [
    ('/freess.html', FreeSS),
    ('/freess/localserver/run/', FreeSSLocalServer, None, 'freess.run'),
    ('/freess/ws/', FreeSSWebSocket, None, 'freess.ws'),
]
