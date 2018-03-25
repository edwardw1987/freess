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


class FreeVPNSS(ShadowsocksResource):
    # url = 'http://freevpnss.cc'
    #url = 'http://get.freevpnss.me'
    url = 'https://get.freevs.org/indexcn.html'

    def iter_params(self, response):
        self.pq = pq(response.content)
        sub_ele = self.pq('.row.text-center')[1]
        sub_pq = pq(sub_ele)
        pat_ip = re.compile(r'服务器地址(?:：|:)[ ]*([\w\.]+)')
        pat_port = re.compile(r'端口(?:：|:)[ ]*(\d+)')
        pat_passwd = re.compile(r'密.*码(?:：|:)[ ]*(\d+)')
        pat_encrypt = re.compile(r'加密方式(?:：|:)[ ]*([\w-]+)')
        patterns = [pat_ip, pat_port, pat_passwd, pat_encrypt]
        panel_body_arr = sub_pq('.panel-body')
        params_groups = []
        for pb in panel_body_arr:
            _html = pq(pb).html().encode('utf-8')
            _couples = []
            for p in patterns:
                findr = p.findall(_html)
                if len(findr) == 0:
                    break
                else:
                    param = findr[0]
                _couples.append(param)
            else:
                params_groups.append(tuple(_couples))
        params_zip = params_groups
        params_zip.sort(key=lambda x: x[0].lower()[0], reverse=True)
        for i in params_zip:
            yield i


class IShadow(ShadowsocksResource):
    #url = "https://global.ishadowx.net/"
    url = "https://en.ishadowx.net/"

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


class ShadowSocks8(ShadowsocksResource):
    url = "http://www.shadowsocks8.com/"

    def iter_params(self, response):
        def handle_resp(response):
            tmp = tempfile.TemporaryFile()
            tmp.write(response.content)
            s = get_QR(tmp)
            _, b64_encoded = s.split('//')
            paramstr = b64_encoded.decode('base64').replace("\n", '')
            encrypt, passwd, ip, port = re.split('[:@]', paramstr)
            ret = (ip, port, passwd, encrypt)
            return ret

        url_tpl = response.url + 'images/server%02d.png'

        def task(i):
            return requests.get(url_tpl % i)

        tasks = [gevent.spawn(task, i + 1) for i in range(3)]
        gevent.joinall(tasks)
        for task in tasks:
            yield handle_resp(task.value)


if __name__ == '__main__':
    disp = Dispatcher(IShadow)
    for i in disp.iter_params():
        print i

