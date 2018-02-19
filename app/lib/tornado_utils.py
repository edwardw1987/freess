from jinja2 import Environment, FileSystemLoader
import tornado.web


class JinjaLoader(object):
    def __init__(self, template_path):
        self.template_path = template_path
        self.jinja_env = None
        self.template = None

    def generate(self, **context):
        if self.template is None:
            return
        template = self.template
        self.template = None
        return template.render(context)

    def load(self, template_name):
        if self.jinja_env is None:
            jinja_env = Environment(
                loader=FileSystemLoader(self.template_path),
                trim_blocks=True,
                extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"])
            self.jinja_env = jinja_env
        else:
            jinja_env = self.jinja_env
        self.template = jinja_env.get_template(template_name)
        return self


class Application(tornado.web.Application):
    def add_handlers_with_prefix(self, host_pattern, host_handlers, url_prefix=None):
        if url_prefix:
            host_handlers = self.add_url_prefix(host_handlers, url_prefix)
        super(Application, self).add_handlers(host_pattern, host_handlers)

    def add_url_prefix(self, handlers, url_prefix):
        ret = []
        for handler in handlers:
            tmp = list(handler)
            tmp[0] = url_prefix.rstrip("/") + tmp[0]
            ret.append(tuple(tmp))
        return ret