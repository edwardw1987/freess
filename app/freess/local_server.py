from collections import deque
import subprocess
import logging
import psutil
import atexit
import os


def init_ports_pool():
    ret = deque(maxlen=10)
    for number in range(2010, 2020):
        ret.append(Port(number))
    return ret


class Port(object):

    def __init__(self, number):
        self.number = number
        self.is_holded = False
        self.pid = None

    def release(self):
        if not self.pid:
            return
        p = psutil.Process(self.pid)
        p.terminate()
        # clear
        self.pid = None
        self.is_holded = False

    def hold_by(self, pid):
        self.pid = pid
        self.is_holded = True


class LocalServer(object):

    ports_pool = init_ports_pool()
    host = "0.0.0.0"
    timeout = 600
    portkeeper = {}

    def __init__(self, paramdict):
        self.paramdict = paramdict

    def get_port(self):
        port = self.ports_pool.popleft()
        if port.is_holded:
            port.release()
        return port

    def put_port(self, port):
        self.ports_pool.append(port)

    def get_cmdlines(self):
        for pid in psutil.pids():
            p = psutil.Process(pid)
            try:
                cmd_arr = p.cmdline()
            except (psutil.AccessDenied, psutil.ZombieProcess):
                continue
            else:
                yield cmd_arr

    def get_pid_file_path(self, port):
        pid_fp = '/tmp/freess%02d.pid' % port
        return pid_fp

    def get_log_file_path(self, port):
        log_fp = '/tmp/freess%02d.log' % port
        return log_fp

    def is_started(self, serverinfo):
        serverinfo = set(serverinfo)
        for cmdline in self.get_cmdlines():
            tmp = []
            for i in cmdline:
                if i in serverinfo:
                    tmp.append(i)
            if set(tmp) == serverinfo:
                return True
        return False

    def start(self):
        """
        param: paramdict:
        {"addr": xx, "port": xx, "key": xx, "encrypt": xx, ...}
        """
        params = self.paramdict
        addr, port, key, encrypt = params["addr"], params["port"], params["key"], params["encrypt"]
        serverinfo = (addr, port, key, encrypt)

        if self.is_started(serverinfo):
            logging.info("alread started: %s:%s" % (addr, port))
            return self.portkeeper[serverinfo]

        one_port = self.get_port()
        local_port = one_port.number
        pid_file = self.get_pid_file_path(local_port)
        log_file = self.get_log_file_path(local_port)

        the_cmdline = ['/usr/bin/python', '/usr/local/bin/sslocal']
        the_cmdline += ['-s', addr]
        the_cmdline += ['-p', port]
        the_cmdline += ['-k', key]
        the_cmdline += ['-m', encrypt]
        the_cmdline += ['-b', self.host]
        the_cmdline += ['-l', str(local_port)]
        the_cmdline += ['-t', str(self.timeout)]
        the_cmdline += ['--pid-file', pid_file]
        the_cmdline += ['--log-file', log_file]
        the_cmdline += ['-d', 'start']


        logging.info("starting: %s:%s" % (addr, port))
        p = psutil.Popen(the_cmdline)
        print '>>>>>>>>>>>>>>>>>>>>>>parent:%s' % os.getpid()
        print '>>>>>>>>>>>>>>>>>>>>>>child:%s' % p.pid
        def tasks():
            print "do>>>>>>>>>>>>>>>>>>>>>>>>>kill %s" % p.pid
            print p.children()
            p.terminate()
            print "do>>>>>>>>>>>>>>>>>>>>>>>>>remove log file %s" % log_file
            os.remove(log_file)
            print "do>>>>>>>>>>>>>>>>>>>>>>>>>remove pid file %s" % pid_file
            os.remove(pid_file)
        atexit.register(tasks)
        one_port.hold_by(p.pid)
        self.put_port(one_port)
        self.portkeeper[serverinfo] = local_port
        return local_port

    def _do_job(self, paramdict):
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
