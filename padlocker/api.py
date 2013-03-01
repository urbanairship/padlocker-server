import json
import netaddr
import os

from flask import Flask, abort, request

import config

app = Flask(__name__)
pad_config = config.PadConfig()

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

    if not netaddr.all_matching_cidrs(request.remote_addr, key_config.get("cidr_ranges", ["0.0.0.0/32"])):
        return False
    
    return True


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


@app.route('/', methods=['GET', 'POST'])
def web_root():
    """Route that administrative users will use."""
    pass

@app.route('/api/<cn>', methods=['POST'])
def get_cn(cn):
    return process_api_post(cn)

if __name__ == '__main__':
    app.debug = True
    app.run(host=pad_config.ip)
