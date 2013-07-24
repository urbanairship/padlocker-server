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

import json

import redis

class Dao(object):
    pass


class RedisBackend(Dao):
    def __init__(self, host='localhost', port=6379):
        self.conn = redis.Redis(host=host, port=port)

    def _make_auth_key(self, cn, ip):
        return '{0}_authorization_for_{1}'.format(cn, ip)

    def enqueue_request(self, cn, ip, value):
        pending_key = '{0}_pending'.format(self._make_auth_key(cn, ip))
        self.conn.set(pending_key, value)
        self.conn.expire(pending_key, 60)

    def get_all_auth_requests(self):
        return [
            json.loads(self.conn.get(item))
                for item in self.conn.keys('*_pending')
        ]

    def authorize_request(self, cn, ip):
        """This function actually marks a CN as authorized for an IP.

        This step requires manual intervention from the web interface.

        """
        key = self._make_auth_key(cn, ip)
        pending_key = '{0}_pending'.format(key)
        self.conn.delete(pending_key)
        self.conn.set(key, True)
        self.conn.expire(key, 5 * 60) # Approvals last for 5 minutes.

    def is_authorized(self, cn, ip):
        return self.conn.get(self._make_auth_key(cn, ip)) is not None

