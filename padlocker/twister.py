#
#   Copyright 2013 Urban Airship
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

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
