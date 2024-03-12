from utils.config import *
from utils.log import log


def get_config(dir, file):
    field_info = {}
    path = os.path.join(dir, file, '.csv')

    with open(path, newline='', encoding='utf-8') as csvfile:
        config = csv.reader(csvfile)
        field_offset = 0

        for row in config:
            field_name, field_length = row[0], int(row[1])
            field_info[field_name] = {'length': field_length, 'offset': field_offset}
            field_offset += field_length

    return field_info


def get_all_config(dir, filelist):
    config = {file: get_config(dir, file) for file in filelist}
    return config

class FormatBase:
    def __init__(self, app_name, exch_config, recv_config, config_path, config_file_list):
        self.id = f"{exch_config['uuid']}:{recv_config['uuid']}"
        self.config_path = os.path.join(CONFIG_DIR, config_path)
        self.config_file_list = config_file_list
        self.config = get_all_config(self.config_path, self.config_file_list)
        self.exch_name, self.data_type, self.feed_type = exch_config['name'], exch_config['type'], recv_config['type']

    @staticmethod
    def parser(config, data, field_name: str):
        if config is None:
            return None

        start, end = config[field_name]['offset'], config[field_name]['offset'] + config[field_name]['length']
        return data[start:end]

class FormatO(FormatBase):
    def __init__(self, app_name, exch_config, recv_config):
        super().__init__(app_name, exch_config, recv_config, 'formatO', ['FUTURE_M', 'OPTION_M', 'SPREAD_M', 'EQUITY_M',
                                                                         'LME_M', 'DEPTH', 'FND', 'QUOTE', 'LME_QUOTE',
                                                                         'LMEWARE_QUOTE', 'STATUS'])
    def classify(self, data):
        if self.exch_name[1:4] == 'LME':
            if self.feed_type == 'M':
                return self.config['LME_M'], 'LME_M'
            if trxc == 'T21':
                return self.config['LME_QUOTE'], 'LME_TRADE'
            elif trxc == 'T40':
                return self.config['LME_QUOTE'], 'LME_SETTLE'
            elif trxc == 'T50':
                return self.config['LME_QUOTE'], 'LME_OINT'
            elif trxc == 'T52':
                return self.config['LME_QUOTE'], 'LME_MAVG'
            elif trxc == 'T60':
                return self.config['LME_QUOTE'], 'LME_OFFI'
            elif trxc == 'T62':
                return self.config['LMEWARE_QUOTE'], 'LME_WARE'
            elif trxc == 'T63':
                return self.config['LMEWARE_QUOTE'], 'LME_VOLM'
            else:
                return None, None
        else:
            if self.feed_type == 'M':
                if self.data_type == 'Equity':
                    return self.config['EQUITY_M'], 'EQUITY_M'
                elif self.data_type == 'Future':
                    return self.config['FUTURE_M'], 'FUTURE_M'
                elif self.data_type == 'Option':
                    return self.config['OPTION_M'], 'OPTION_M'
                elif self.data_type == 'Spread':
                    return self.config['SPREAD_M'], 'SPREAD_M'
                else:
                    return None, None
            else:
                trxc = data[0:4]

                if trxc == 'T60':
                    return self.config['STATUS'], 'STATUS'
                elif trxc == 'T21':
                    return self.config['QUOTE'], 'TRADE'
                elif trxc == 'T24':
                    return self.config['QUOTE'], 'CANCEL'
                elif trxc == 'T40':
                    return self.config['QUOTE'], 'SETTLE'
                elif trxc == 'T41':
                    return self.config['QUOTE'], 'CLOSE'
                elif trxc == 'T50':
                    return self.config['QUOTE'], 'OINT'
                elif trxc == 'T31':
                    return self.config['DEPTH'], 'DEPTH'
                elif trxc == 'T80':
                    return self.config['FND'], 'FND'
                else:
                    return None, None


    def validation(self, data):
        config, class_name = self.classify(data)
        return True


class FormatH():
    def __init__(self, app_name, exch_config, recv_config):
        super().__init__(app_name, exch_config, recv_config, 'formatH', ['FUTURE_M', 'OPTION_M', 'FUTURE_DEPTH',
                                                                         'OPTION_DEPTH', 'FUTURE_QUOTE', 'OPTION_QUOTE',
                                                                         'FUTURE_SETTLE', 'OPTION_SETTLE'])

    def classify(self, data):
        pass

    def validation(self, data):
        config, class_name = self.classify(data)
        return True



class FormatE():
    def __init__(self, app_name, exch_config, recv_config):
        super().__init__(app_name, exch_config, recv_config, 'formatE', ['FUTURE_M', 'OPTION_M', 'DEPTH', 'QUOTE',
                                                                         'SPREAD_M'])

    def classify(self, data):
        pass

    def validation(self, data):
        config, class_name = self.classify(data)
        return True

class Format():
    def __init__(self, app_name, exch_config, recv_config):
        self.app_name, self.exch_config, self.recv_config = app_name, exch_config, recv_config
        self.exch_type, self.recv_type, self.format = exch_config['type'], recv_config['type'], recv_config['format']
        self.is_valid, self.id = False, f"{exch_config['uuid']}:{recv_config['uuid']}"
        self.formatO = FormatO(app_name, exch_config, recv_config)
        self.formatH = FormatH(app_name, exch_config, recv_config)
        self.formatE = FormatE(app_name, exch_config, recv_config)


    def validation(self, data):
        try:
            if self.format == "old":
                self.is_valid = self.formatO.validation(data)
            elif self.format == 'hana':
                self.is_valid = self.formatH.validation(data)
            elif self.format == 'ext':
                self.is_valid = self.formatE.validation(data)

            return self.is_valid
        except Exception:
            return False


    def classify(self, data):
        try:
            if self.format == "old":
                config, class_name = self.formatO.classify(data)
            elif self.format == 'hana':
                config, class_name = self.formatH.classify(data)
            elif self.format == 'ext':
                config, class_name = self.formatE.classify(data)

            if config is None or class_name is None:
                return None, None

            return config, class_name
        except Exception:
            return None, None


    def convert_csv(self, data):
        try:
            csv_data = None
            config, class_name = self.classify(data)

            if config is None:
                return None

            data_list = [data[value['offset']:value['offset'] + value['length']]
                         for key, value in config.items()]

            csv_data = ','.join(map(str, data_list))
            return csv_data
        except Exception as e:
            log(self.app_name, f"Failed to convert data to CSV: {str(e)}")
            return None
