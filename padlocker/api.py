import json

from flask import Flask, abort, request

import netaddr

app = Flask(__name__)

#
## These are arguements that we should fill in from a settings file.
###
CERT_REQUEST_NAME = 'KEY_REQ'
CIDR_IPS = (
    '127.0.0.1/24',
    '10.0.0.0/8',
    '192.168.0.1/24',
)
KNOWN_CERT_COMMON_NAMES = (
    'test'
)

def process_get():
    return json.dumps(KNOWN_CERT_COMMON_NAMES)


def is_permitted():
    return bool(netaddr.all_matching_cidrs(request.remote_addr, CIDR_IPS))


def read_file(common_name):
    with open('certs/{0}'.format(common_name)) as f:
        cert_data = f.read()

    return cert_data


def process_post():
    if not is_permitted():
        abort(403)
    try:
        cert_requests = json.loads(request.form.get(CERT_REQUEST_NAME), '')
    except:
        abort(400)

    if len(cert_requests.keys()) > 1:
        # We should only be requesting one cert at a time.
        abort(400)

    for common_name, meta_data in cert_requests.items():
        if common_name in KNOWN_CERT_COMMON_NAMES:
            return read_file(common_name)


@app.route('/', methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        return process_post()

    return process_get()

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
