from utils.config import *

class Format():
    def __init__(self, app_name, exch_config, recv_config):
        self.app_name = app_name
        self.exch_config = exch_config
        self.recv_config = recv_config
        self.exch_type = exch_config['type']
        self.recv_type = recv_config['type']
        self.format = recv_config['format']

    def validation(self, data):
        if self.format == "old":
            pass
        elif self.format == 'hana':
            pass
