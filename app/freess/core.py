# -*- coding: utf-8 -*-
# @Author: edward
# @Date:   2016-12-03 18:02:57
# @Last Modified by:   edward
# @Last Modified time: 2018-09-26 22:32:10
import logging
import socket
import subprocess
import time
import requests

requests.packages.urllib3.disable_warnings()
socket.setdefaulttimeout(5)


class Resource(object):
    url = None
    proxy = None
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    def get_response(self):
        proxy = getattr(self, "proxy")
        url = getattr(self, "url")
        if not url:
            return
        params = dict(
            url=url,
            timeout=3,
            headers=self.headers,
            verify=False,
            #allow_redirects=False,
        )
        if proxy:
            params["proxies"] = {'http': proxy}
        resp = requests.get(**params)
        #if resp.status_code != 200:
        #    params["url"] = resp.headers["location"]
        #    del params["allow_redirects"]
        #    resp = requests.get(**params)
        logging.info("***url %s" % resp.url)
        logging.info("***%s" % resp.content)
        return resp


job_count = 86


def get_cmd_by_port(cmd_prefix, port):
    port = int(port)
    pid_file = '/tmp/freess%02d.pid' % port
    log_file = '/tmp/freess%02d.log' % port
    the_cmd_tpl = cmd_prefix + ' -l %s -t 600 --pid-file %s --log-file %s -d restart'
    cmdstr = the_cmd_tpl % (port, pid_file, log_file)
    return cmdstr


def run_cmd_by_port(cmd_prefix, port):
    cmdstr = get_cmd_by_port(cmd_prefix, port)
    try:
        pro = subprocess.call(cmdstr, shell=True)
    except:
        return
    return 0


def is_cmd_run_on_port(cmd_prefix, port):
    cmdstr = get_cmd_by_port(cmd_prefix, port)
    pro = subprocess.Popen('ps -x|grep " -l %s"' % int(port), shell=True, stdout=subprocess.PIPE)
    pro.wait()
    return cmdstr in pro.stdout.read()


PORTS = (
    1987,
    1988,
)


class ShadowsocksResource(Resource):
    def iter_params(self, response):
        raise NotImplementedError()

    def iter_jobs(self):
        # self.iter_params(self.get_response())
        for param in self.iter_params(self.get_response()):
            param_dict = {"addr": param[0], "port": param[1],
                          "key": param[2], "encrypt": param[3]}
            yield (self._do_job, param_dict)

    def _do_job(self, paramdict):
        # make cmd
        global job_count
        if job_count >= 92:
            job_count = 86
        job_count += 1
        cmd_tpl = "/usr/local/bin/sslocal -s {addr} -p {port} -k {key} -m {encrypt} -b %s -l %s -t %s --pid-file %s --log-file %s -d %s"
        cmd_tpl = cmd_tpl.format(**paramdict)
        port = "55%02d" % job_count
        pid_file = '/tmp/freess%02d.pid' % job_count
        log_file = '/tmp/freess%02d.log' % job_count
        param = ("0.0.0.0", port, 600, pid_file, log_file, 'start')
        # param = ("127.0.0.1", port, 600)
        cmdstr = cmd_tpl % param
        logging.info("cmdstr:%s" % cmdstr)

        paramdict["cmd"] = cmdstr.partition(' -l')[0]
        paramdict["ports"] = []
        paramdict["status"] = "fail"
        paramdict["delay"] = "n/a"
        paramdict["tries"] = 15
        # 
        for active_port in PORTS:
            if is_cmd_run_on_port(paramdict["cmd"], active_port):
                paramdict["ports"].append(active_port)
        # call cmd
        logging.info("before: %s" % cmdstr)
        output = subprocess.call(cmdstr, shell=True)
        logging.info("after: %s" % output)

        def check_status(tries=1):
            print 'INFO: TRY %d check %s' % (tries, "socks5://127.0.0.1:%s" % port)
            try:
                ss = requests.Session()
                start = time.clock()
                resp = ss.get('http://www.google.com',
                              timeout=5,
                              proxies={"http": "socks5://127.0.0.1:%s" % port})
                end = time.clock()
            except requests.exceptions.ConnectionError:
                if tries < 15:
                    tries += 1
                    return check_status(tries)
            except IOError as err:
                print err
            except requests.exceptions.Timeout:
                pass
            else:
                paramdict["status"] = "ok"
                paramdict["delay"] = '%dms' % (round(end - start, 3) * 1000)
            paramdict["tries"] = tries

        check_status()
        output = subprocess.check_output(
            "ps -x|grep '%s'" % cmdstr, shell=True)
        the_pid = output.split(None, 1)[0]
        pro = subprocess.Popen("kill %d" % int(the_pid), shell=True)
        pro.wait()
        return paramdict

    @classmethod
    def fetch_all(cls):
        ret = [v for v in cls.__subclasses__()]
        return ret


if __name__ == '__main__':
    print get_country_by_addr('188.166.186.129')
