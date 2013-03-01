import re
ip = '0.0.0.0'
key_dir = 'keys'
key_configs = {
    'a-server.example.com': {
        'cidr_ranges': ['128.0.0.1/24'],
    },
    'b-server.example.com': {
        'cidr_ranges': ['0.0.0.0/0'],
        'service': 'b-server',
        'path': [re.compile(r".*key$"), lambda x: False]
    }
}
