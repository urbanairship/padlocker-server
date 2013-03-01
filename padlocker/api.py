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

KNOWN_KEY_COMMON_NAMES = get_key_names()

def process_get():
    return json.dumps(KNOWN_KEY_COMMON_NAMES)


def is_permitted(common_name):
    cidr_ranges = pad_config.key_configs.get(common_name) or []
    return bool(netaddr.app_matching_cidrs(request.remote_addr, cidr_ranges))


def read_file(common_name):
    with open('{0}/{1}'.format(pad_config.key_dir, common_name)) as f:
        key_data = f.read()

    return key_data


def process_post():
    if not is_permitted():
        abort(403)
    try:
        key_requests = json.loads(request.data)
    except:
        abort(400)

    if len(key_requests.keys()) > 1:
        # We should only be requesting one key at a time.
        abort(400)

    for common_name, meta_data in key_requests.items():
        if common_name in KNOWN_KEY_COMMON_NAMES:
            return read_file(common_name)


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        return process_post()

    return process_get()

if __name__ == '__main__':
    app.debug = True
    app.run(host=pad_config.ip)
