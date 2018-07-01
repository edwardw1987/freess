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
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        }
        if not url:
            return
        params = dict(
            url=url,
            timeout=3,
            headers=headers
        )
        if proxy:
            params["proxies"] = {'http': proxy}
        resp = requests.get(**params)
        # if resp.status_code != 200:
        #     params["url"] = resp.headers["location"]
        #     del params["allow_redirects"]
        #     resp = requests.get(**params)
        return resp

