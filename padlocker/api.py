import json
import netaddr
import os
import redis

from flask import Flask, abort, request, render_template

import config

app = Flask(__name__)
pad_config = config.PadConfig()

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
def get_redis_conn():
    conn = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    return conn

REDIS = get_redis_conn()


def get_key_names():
    return [
        file for file in os.listdir(pad_config.key_dir)
        if not file.startswith('.')
    ]


def process_api_get():
    return json.dumps(get_key_names())


def is_permitted(cn, req):
    key_config = pad_config.key_configs.get(cn)

    if not key_config:
        return False

    if not netaddr.all_matching_cidrs(
        request.remote_addr, key_config.get("cidr_ranges", ["0.0.0.0/32"])
    ):
        return False

    return True

def request_authorization(cn, req):
    """The request is permitted, but now we need approval to return the key."""
    REDIS.lpush('approval_queue', json.dumps(
        {'cn': cn, 'ip': req.request_addr, 'service': req.data.get('service', '')}
    ))
    #REDIS.expire('approval_queue', 60) # TTL of only a minute.

    return 'request for approval received'


def _make_auth_key(cn, ip):
    return '{0}_authorization_for_{1}'.format(cn, ip)


def get_authorization_requests():
    return [json.loads(item) for item in REDIS.lrange('approval_queue', 0, -1)]


def authorize_request(cn, ip):
    """This function actually marks a CN as authorized for an IP.

    This step requires manual intervention from the web interface.

    """
    key = _make_auth_key(cn, ip)
    REDIS.set(key, True)
    REDIS.expire(key, 5 * 60) # Approvals last for 5 minutes.


def is_authorized(cn, ip):
    return REDIS.get(_make_auth_key(cn, ip)) is not None


def read_file(cn):
    with open('{0}/{1}'.format(pad_config.key_dir, cn)) as f:
        key_data = f.read()

    return key_data


def process_api_post(cn):
    try:
        req = json.loads(request.data)
    except:
        abort(400)

    if not is_permitted(cn, req):
        abort(403)

    if cn in get_key_names():
        return read_file(cn)


class Approval(object):
    """A context object for our webforms."""
    def __init__(self, *args, **kwargs):
        self.cn = kwargs.get('cn', '')
        self.ip = kwargs.get('ip', '')
        self.service = kwargs.get('service', '')
        payload = kwargs.get('payload', {})
        for item in payload:
            self.__setattr__(item, payload[item])


def get_fake_auth_requests(x=5):
    return sorted([
        Approval('fake-cn-{0}.example.com'.format(i), '127.0.0.1', 'test_service')
        for i in range(x)
    ],
    key=lambda approval: approval.cn
    )


@app.route('/', methods=['GET', 'POST'])
def web_root():
    """Route that administrative users will use."""
    auth_requests = [
        Approval(payload=request) for request in get_authorization_requests()
    ]
    return render_template('index.html', auth_requests=auth_requests)


@app.route('/api/<cn>', methods=['POST'])
def get_cn(cn):
    return process_api_post(cn)

if __name__ == '__main__':
    app.debug = True
    app.run(host=pad_config.ip)
