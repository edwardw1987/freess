#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: edward
# @Date:   2015-12-06 09:42:12
# @Last Modified by:   edward
# @Last Modified time: 2016-12-03 12:56:56
import urllib
import os
import sys
import re
import socket
import random
import signal
from urlparse import urlparse
from pyquery import PyQuery as pq
from multiprocessing import cpu_count
import argparse


def check_server(address, port):
    # Create a TCP socket
    socket.setdefaulttimeout(3)
    s = socket.socket()
    print "Attempting to connect to %s on port %s" % (address, port)
    try:
        s.connect((address, port))
        print "Connected to %s on port %s" % (address, port)
        return True
    except socket.error, e:
        print "Connection to %s on port %s failed: %s" % (address, port, e)
        return False


class ShadowsocksServer:
    choose = -1
    test_proxy_maximum = 5
    timeout = 600
    local_port = 1987
    local_addr = '127.0.0.1'
    urls = [
        #'http://www.ishadowsocks.net/',
        #'http://i.freevpnss.com/',
        'http://freevpnss.cc'
    ]

    def __init__(self, **kwargs):
        self._test_counter = 0
        self._html = None
        self.pq = None
        self._launched = False
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def _crawl_page(self):
        urls = self.urls[:]
        random.shuffle(urls)
        for url in urls:
            _proxy = getattr(self, "proxy", None)
            if _proxy is None:
                resp = urllib.urlopen(url)
            else:
                resp = urllib.urlopen(url, proxies={'http': _proxy})
            if resp.code == 200:
                print 'Free proxy crawling from %r' % urlparse(url).hostname
                self._html = resp.read()
                self.pq = pq(self._html)
                break
        else:
            print 'failed in crawling any free-proxy pages!'
            exit(1)

    def _check_params(self, params):
        _params = tuple(params)
        if all(_params):
            return _params
        else:
            raise Exception('{} exists invalid parameter!'.format(_params))

    def iter_params(self):
        return self._ext_params()

    def _ext_params(self):
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

    def _check_sock5_proxy(self, addr, port):
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, addr=addr, port=port)
        socket.socket = socks.socksocket

        def signal_handler(signum, frame):
            raise Exception("Timed out!")

        signal.signal(signal.SIGALRM, signal_handler)
        signal.alarm(3)

        try:
            resp = urllib.urlopen(url="http://www.google.com")
        except IOError:
            return 1
        except Exception, msg:
            print "Timed out!"
            if self._test_counter < self.test_proxy_maximum:
                self._test_counter += 1
                print "test proxy...%d" % self._test_counter
                return self._check_sock5_proxy(addr, port)
            else:
                print 'Sorry, all tests failed! \nMaybe the localserver launched but the speed is not ideal!'
                exit(1)

        if resp.code == 200:
            print 'test ok!'
            return 0
        print 'test failed'
        return 1

    def _handle_act(self):
        if sys.platform.startswith('win'):
            return
        if self._launched is False:
            try:
                act = self.daemon_mode
                assert act in ('start', 'restart')
            except AssertionError:
                raise IndexError('invalid "act" param (start/restart)!')
        else:
            act = 'restart'
        return act

    def execute(self, params):
        act = self._handle_act()
        _params = list(params)
        teps = dict(
            local_port=self.local_port,
        )
        launch_cmd = "sslocal -s %s -p %s -k %s -m %s -b %s -l %s -t %s"
        if sys.platform == 'linux2':
            launch_cmd += ' --pid-file %s --log-file %s -d %s'
            teps.update(
                pid_file='/tmp/freess%02d.pid',
                log_file='/tmp/freess%02d.log',
            )
        for i in range(cpu_count()):
            execute_params = _params[:]
            execute_params.extend([
                self.local_addr,
                teps['local_port'] + i,
                self.timeout,
                teps['pid_file'] % (i + 1),
                teps['log_file'] % (i + 1),
                act,
            ])
            os.system(launch_cmd % tuple(execute_params))
        self._launched = True

    def get_router(self):
        ISP = {
            "192.168.1.1": "中国电信",
            "192.168.100.1": "中国移动"
        }
        for addr in ISP:
            signal = check_server(addr, 80)
            if signal is True:
                print "你使用的是%s网络。" % ISP[addr]
                break
        else:
            print "网络未知"

    def serve(self):
        self.get_router()
        self._handle_act()
        self._crawl_page()

        params_array = [(idx, params)
                        for idx, params in enumerate(self.iter_params())]
        params_index = -1
        # if self.choose:
        #     prompt_str = '\r\n'.join(map(
        #         lambda x: str(x[0]) + '.' + str(x[1]), params_array))
        #     params_index = raw_input(prompt_str + '\r\nchoose? ') or 0
        #     params_index = int(params_index)
        print params_array
        self.execute(params=self._check_params(params_array[self.choose][1]))
        # signal = self._check_sock5_proxy('localhost', self.local_port)
        # if signal == 1:
        #     continue
        # elif signal == 0:
        #     return
    # else:
        # servername = self.__class__.__name__
        # print '{} launched failed!'.format(servername)
        # exit(1)


def main():
    parser = argparse.ArgumentParser(description="freess")
    parser.add_argument('-d', dest='daemon_mode', required=False,
                        default="start", action='store', help="start|restart")
    parser.add_argument('--choose', dest='choose', required=False, type=int,
                        action='store', default="-1", help="choose a remote server")
    parser.add_argument('-x', dest='proxy', required=False,
                        action="store", help="use http proxy")
    args = parser.parse_args()
    server = ShadowsocksServer(
        choose=args.choose, daemon_mode=args.daemon_mode, proxy=args.proxy)
    server.serve()
if __name__ == '__main__':
    main()
