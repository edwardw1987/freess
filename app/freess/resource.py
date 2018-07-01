#!/usr/bin/env python
# coding: utf-8
import re
import tempfile

import gevent
import requests
from PIL import Image
from gevent import socket
from pyquery import PyQuery as pq



class ShadowsocksResource(object):

    def iter_params(self, response):
        raise NotImplementedError()

class IShadow(ShadowsocksResource):
    #url = "https://global.ishadowx.net/"
    url = "http://ss.ishadowx.com/"

    def iter_params(self, response):
        self.pq = pq(response.content)
        params_groups = []
        u = []
        for hover_text_div in self.pq('.hover-text'):
            htd_pq = pq(hover_text_div)
            addr = htd_pq.children('h4').eq(0).children('span').eq(0).text()
            port = htd_pq.children('h4').eq(1).children('span').eq(0).text().strip()
            password = htd_pq.children('h4').eq(2).children('span').eq(0).text()
            method = htd_pq.children('h4').eq(3).text().split(u'Method:')[-1].strip()
            e = [addr, port, password, method]
            if len([i for i in e if i.strip() == ""]):
                continue
            e.append(self.get_encoded(addr, port, password, method))
            if e not in u:
                u.append(e)
        for i in sorted(u):
            yield i
        # params_zip = params_groups
        # params_zip.sort(key=lambda x: x[0].lower()[0], reverse=True)
        # for i in params_zip:
        #     yield i

    def get_encoded(self, addr, port, password, method):
        pork = "{method}:{password}".format(**locals())
        cooked = pork.encode("base64")
        cooked = cooked.strip("\n")
        # print pork
        # print cooked
        tpl = "ss://{cooked}@{addr}:{port}"
        return tpl.format(**locals())

    def decode(self, encoded):
        base64_en = encoded.split("//")[1].split("@")[0]
        return (base64_en + "=").decode("base64")


if __name__ == '__main__':
    from dispatcher import Dispatcher
    disp = Dispatcher(IShadow)
    for i in disp.iter_params():
        print i

