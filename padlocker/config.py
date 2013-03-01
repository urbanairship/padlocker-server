class PadConfig(object):
    ip = '127.0.0.1'
    key_dir = 'keys'

    def __init__(self):
        import settings
        self.ip = settings.ip or  PadConfig.ip
        self.key_dir = settings.key_dir or PadConfig.key_dir
        self.key_configs = settings.key_configs or {}
