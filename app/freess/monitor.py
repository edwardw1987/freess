import requests
import gevent
from gevent import monkey

monkey.patch_all()

class Monitor(object):
    ports = [
        1080,
        1987
    ]
    test_urls = [
        "http://www.google.com",
    ] * 2

    def test_port(self, port, url):
        ret = {"port": port}
        try:
            resp = requests.get(url, proxies={
                "http": "socks5://localhost:%d" % port
                })
            ret["success"] = True
        except Exception:
            ret["success"] = False
        return ret

    def run(self):
        ret = {port:{} for port in self.ports}
        cnt = 0
        max_continous_success = 0
        for i in range(10):
            cnt += 1
            jobs = [gevent.spawn(self.test_port, port, url) for port in self.ports for url in self.test_urls]
            gevent.joinall(jobs)
            for job in jobs:
                jobval = job.value
                success = jobval["success"]
                port = jobval["port"]
                if success:
                    ret[port]["pass"] = ret[port].get("pass", 0) + 1
                else:
                    ret[port]["fail"] = ret[port].get("fail", 0) + 1
            outputs = ["port:%d stat:%s rate:%.2f%%" % (
                k, v, 100 * float(v.get("pass", 0))/(v.get("pass", 0) + v.get("fail",0)
                    )) for k, v in ret.items()]
            print "\n".join(outputs)


if __name__ == '__main__':
    mo = Monitor()
    mo.run()