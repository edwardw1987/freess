import requests


class Dispatcher(object):

    def __init__(self, resource_cls, proxy=None):
        self.proxy = proxy
        self.resource = resource_cls()

    def iter_params(self):
        """
        return generator
        addr, port, key, encrypt, uri
        """
        res = self.resource
        resp = self._fetch_resource(res)
        return res.iter_params(resp)

    def _fetch_resource(self, res):
        url = getattr(res, 'url', None)
        proxy = self.proxy
        if not url:
            return
        params = dict(
            url=url,
            timeout=3,
            allow_redirects=False,
        )
        if proxy:
            params["proxies"] = {'http': proxy}
        resp = requests.get(**params)
        if resp.status_code != 200:
            params["url"] = resp.headers["location"]
            del params["allow_redirects"]
            resp = requests.get(**params)
        return resp

