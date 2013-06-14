import os

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import FallbackHandler, Application
from tornado.wsgi import WSGIContainer

import api

SSL = False

flasker = WSGIContainer(api.app)

application = Application([
    (r'.*', FallbackHandler, dict(fallback=flasker)),
])

http_server = application

if SSL:
    # This is basically just a placeholder.
    http_server = HTTPServer(
        application,
        ssl_options={
            'certfile': os.path.join('.', 'padlocker.cert'),
            'keyfile': os.path.join('.', 'padlocker.key'),
        }
    )

if __name__ == '__main__':
    http_server.listen(5000)
    IOLoop.instance().start()
