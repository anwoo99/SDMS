from utils.config import *
from utils.log import log

class Format():
    def __init__(self, app_name, exch_config, recv_config):
        self.app_name = app_name
        self.exch_config = exch_config
        self.recv_config = recv_config
        self.exch_type = exch_config['type']
        self.recv_type = recv_config['type']
        self.format = recv_config['format']
        self.is_valid = False
        self.id = f"{exch_config['uuid']}:{recv_config['uuid']}"

    def __read_format_csv(self, filename):
        try:
            pass
        except Exception:
            return None

    def __read_formatO(self):
        try:
            pass
        except Exception:
            log(self.app_name, f"Failed to read formatO csv for({self.id})")
            return None

    def __read_formatH(self):
        try:
            pass
        except Exception:
            log(self.app_name, f"Failed to read formatH csv for({self.id})")
            return None
        
    def __read_formatE(self):
        try:
            pass
        except Exception:
            log(self.app_name, f"Failed to read formatE csv for({self.id})")
            return None

    def __old_validation(self, data):
        try:
            return True
        except Exception:
            return False
        
    def __hana_validation(self, data):
        try:
            return True
        except Exception:
            return False
        
    def __ext_validation(self, data):
        try:
            return True
        except Exception:
            return False
        
    def validation(self, data):
        try:
            if self.format == "old":
                self.is_valid = self.__old_validation()
            elif self.format == 'hana':
                self.is_valid = self.__hana_validation()
            elif self.format == 'ext':
                self.is_valid = self.__ext_validation()
            
            return self.is_valid
        except Exception:
            return False
    
    def parser(self, data, field_name:str):
        try:
            pass
        except Exception:
            log(self.app_name, f"Failed to pasing data for({self.id})")

    def convert_csv(self, data):
        pass
