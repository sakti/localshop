from gunicorn.app.djangoapp import DjangoApplication
from gunicorn.arbiter import Arbiter
import sys

from localshop.services.base import Service


class LocalShopApplication(DjangoApplication):
    def __init__(self, options):
        self.usage = None
        self.cfg = None
        self.config_file = options.get("config") or ""
        self.options = options
        self.callable = None
        self.project_path = None

        self.do_load_config()

        for k, v in self.options.items():
            if k.lower() in self.cfg.settings and v is not None:
                self.cfg.set(k.lower(), v)

    def init(self, parser, opts, args):
        pass

    def load(self):
        from localshop.wsgi import application
        import eventlet.patcher

        eventlet.patcher.monkey_patch()

        self.activate_translation()

        return application


class LocalShopHTTPServer(Service):
    name = 'http'

    def __init__(self, host=None, port=None, debug=False, daemonize=False,
                 pidfile=None, logfile=None):
        from localshop.conf import settings

        self.host = host or settings.WEB_HOST
        self.port = port or settings.WEB_PORT

        self.app = LocalShopApplication({
            'bind': '%s:%s' % (self.host, self.port),
            'debug': debug,
            'daemon': daemonize,
            'pidfile': pidfile,
            'errorlog': logfile,
        })

    def run(self):
        try:
            Arbiter(self.app).run()
        except RuntimeError, e:
            sys.stderr.write("\nError: %s\n\n" % e)
            sys.stderr.flush()
            sys.exit(1)

    start = run

