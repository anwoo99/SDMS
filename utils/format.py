from utils.config import *
from utils.log import log

def formatO_validation(config, class_name):
    """
    필요한 valdiation을 기입하세요. 
    Return은 반드시 (is_valid(boolean), reason(str)) 으로 작성하세요.
    """
    is_valid = True
    reason = None

    try:
        if class_name is None or config is None:
            return False, "Unknown data type"
        
        if class_name == "OLD_LME_M":
            pass
        elif class_name == 'OLD_LME_TRADE':
            pass
        elif class_name == 'OLD_LME_SETTLE':
            pass
        elif class_name == 'OLD_LME_OINT':
            pass
        elif class_name == 'OLD_LME_MAVG':
            pass
        elif class_name == 'OLD_LME_OFFI':
            pass
        elif class_name == 'OLD_LME_WARE':
            pass
        elif class_name == 'OLD_LME_VOLM':
            pass
        elif class_name == 'OLD_EQUITY_M':
            pass
        elif class_name == 'OLD_FUTURE_M':
            pass
        elif class_name == 'OLD_OPTION_M':
            pass
        elif class_name == 'OLD_SPREAD_M':
            pass
        elif class_name == 'OLD_STATUS':
            pass
        elif class_name == 'OLD_TRADE':
            pass
        elif class_name == 'OLD_CANCEL':
            pass
        elif class_name == 'OLD_SETTLE':
            pass
        elif class_name == 'OLD_CLOSE':
            pass
        elif class_name == 'OLD_OINT':
            pass
        elif class_name == 'OLD_DEPTH':
            pass
        elif class_name == 'OLD_FND':
            pass

        return is_valid, reason
    except Exception as err:
        return False, "Failed to validation for formatO"


def formatH_validation(config, class_name):
    """
    필요한 valdiation을 기입하세요. 
    Return은 반드시 (is_valid(boolean), reason(str)) 으로 작성하세요.
    """
    is_valid = True
    reason = None

    try:
        if class_name is None or config is None:
            return False, "Unknown data type"

        return is_valid, reason
    except Exception as err:
        return False, "Failed to validation for formatH"


def formatE_validation(config, class_name):
    """
    필요한 valdiation을 기입하세요. 
    Return은 반드시 (is_valid(boolean), reason(str)) 으로 작성하세요.
    """
    is_valid = True
    reason = None

    try:
        if class_name is None or config is None:
            return False, "Unknown data type"

        return is_valid, reason
    except Exception as err:
        return False, "Failed to validation for formatE"


def get_config(dir, file):
    field_info = {}
    path = os.path.join(dir, file + '.csv')

    try:
        with open(path, newline='', encoding='utf-8') as csvfile:
            config = csv.reader(csvfile)
            field_offset = 0

            for row in config:
                if not row:
                    continue

                field_name, field_length = row[0], int(row[1])

                if field_name in field_info:  # Check if the field_name is already in field_info
                    raise Exception(f"{field_name} is duplicated in '{path}'")

                field_info[field_name] = {'length': field_length, 'offset': field_offset}
                field_offset += field_length

        return field_info
    except Exception as err:
        raise


def get_all_config(dir, filelist):
    try:
        config = {file: get_config(dir, file) for file in filelist}
        return config
    except Exception:
        raise

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
                return self.config['LME_M'], 'OLD_LME_M', 'MASTER'
            if trxc == 'T21':
                return self.config['LME_QUOTE'], 'OLD_LME_TRADE', 'QUOTE'
            elif trxc == 'T40':
                return self.config['LME_QUOTE'], 'OLD_LME_SETTLE', 'QUOTE'
            elif trxc == 'T50':
                return self.config['LME_QUOTE'], 'OLD_LME_OINT', 'QUOTE'
            elif trxc == 'T52':
                return self.config['LME_QUOTE'], 'OLD_LME_MAVG', 'QUOTE'
            elif trxc == 'T60':
                return self.config['LME_QUOTE'], 'OLD_LME_OFFI', 'QUOTE'
            elif trxc == 'T62':
                return self.config['LMEWARE_QUOTE'], 'OLD_LME_WARE', 'QUOTE'
            elif trxc == 'T63':
                return self.config['LMEWARE_QUOTE'], 'OLD_LME_VOLM', 'QUOTE'
            else:
                return None, None, None
        else:
            if self.feed_type == 'M':
                if self.data_type == 'Equity':
                    return self.config['EQUITY_M'], 'OLD_EQUITY_M', 'MASTER'
                elif self.data_type == 'Future':
                    return self.config['FUTURE_M'], 'OLD_FUTURE_M', 'MASTER'
                elif self.data_type == 'Option':
                    return self.config['OPTION_M'], 'OLD_OPTION_M', 'MASTER'
                elif self.data_type == 'Spread':
                    return self.config['SPREAD_M'], 'OLD_SPREAD_M', 'MASTER'
                else:
                    return None, None, None
            else:
                trxc = data[0:3]

                if trxc == 'T60':
                    return self.config['STATUS'], 'OLD_STATUS', 'STATUS'
                elif trxc == 'T21':
                    return self.config['QUOTE'], 'OLD_TRADE', 'QUOTE'
                elif trxc == 'T24':
                    return self.config['QUOTE'], 'OLD_CANCEL', 'QUOTE'
                elif trxc == 'T40':
                    return self.config['QUOTE'], 'OLD_SETTLE', 'SETTLE'
                elif trxc == 'T41':
                    return self.config['QUOTE'], 'OLD_CLOSE', 'CLOSE'
                elif trxc == 'T50':
                    return self.config['QUOTE'], 'OLD_OINT', 'QUOTE'
                elif trxc == 'T31':
                    return self.config['DEPTH'], 'OLD_DEPTH', 'DEPTH'
                elif trxc == 'T80':
                    return self.config['FND'], 'OLD_FND', 'FND'
                else:
                    return None, None, None


    def validation(self, data):
        config, class_name = self.classify(data)
        is_valid, reason = formatO_validation(config, class_name)
        return is_valid, reason


class FormatH(FormatBase):
    def __init__(self, app_name, exch_config, recv_config):
        super().__init__(app_name, exch_config, recv_config, 'formatH', ['FUTURE_M', 'OPTION_M', 'FUTURE_DEPTH', 
                                                                         'OPTION_DEPTH', 'FUTURE_QUOTE', 'OPTION_QUOTE',
                                                                         'FUTURE_SETTLE', 'OPTION_SETTLE'])

    def classify(self, data):
        type = data[0:2]

        if type == "fb":
            return self.config['FUTURE_M'], 'HANA_FUTURE_M', 'MASTER'
        elif type == "ob":
            return self.config['OPTION_M'], 'HANA_OPTION_M', 'MASTER'
        elif type == "fc":
            return self.config['FUTURE_QUOTE'], 'HANA_FUTURE_QUOTE', 'QUOTE'
        elif type == "oc":
            return self.config['OPTION_QUOTE'], 'HANA_OPTION_QUOTE', 'QUOTE'
        elif type == 'fh':
            return self.config['FUTURE_DEPTH'], 'HANA_FUTURE_DEPTH', 'DEPTH'
        elif type == 'oh':
            return self.config['OPTION_DEPTH'], 'HANA_OPTION_DEPTH', 'DEPTH'
        elif type == 'fu':
            return self.config['FUTURE_SETTLE'], 'HANA_FUTURE_SETTLE', 'SETTLE'
        elif type == 'ou':
            return self.config['OPTION_SETTLE'], 'HANA_OPTION_SETTLE', 'SETTLE'
        else:
            return None, None, None
        

    def validation(self, data):
        config, class_name, _ = self.classify(data)
        is_valid, reason = formatH_validation(config, class_name)
        return is_valid, reason



class FormatE(FormatBase):
    def __init__(self, app_name, exch_config, recv_config):
        super().__init__(app_name, exch_config, recv_config, 'formatE', ['FUTURE_M', 'OPTION_M', 'DEPTH', 'QUOTE',
                                                                         'SPREAD_M'])

    def classify(self, data):
        if self.feed_type == 'M':
            if self.data_type == 'Future':
                return self.config['FUTURE_M'], 'EXT_FUTURE_M', 'MASTER'
            elif self.data_type == 'Option':
                return self.config['OPTION_M'], 'EXT_OPTION_M', 'MASTER'
            elif self.data_type == 'Spread':
                return self.config['SPREAD_M'], 'EXT_SPREAD_M', 'MASTER'
            else:
                return None, None, None
        else:
            trxc = data[0:3]

            if trxc == 'T21':
                return self.config['QUOTE'], 'EXT_TRADE', 'QUOTE'
            elif trxc == 'T40':
                return self.config['QUOTE'], 'EXT_SETTLE', 'SETTLE'
            elif trxc == 'T41':
                return self.config['QUOTE'], 'EXT_CLOSE', 'CLOSE'
            elif trxc == 'T50':
                return self.config['QUOTE'], 'EXT_OINT', 'QUOTE'
            elif trxc == 'T31':
                return self.config['DEPTH'], 'EXT_DEPTH', 'DEPTH'
            else:
                return None, None, None


    def validation(self, data):
        config, class_name, _ = self.classify(data)
        is_valid, reason = formatE_validation(config, class_name)
        return is_valid, reason

class Format():
    def __init__(self, app_name, exch_config, recv_config):
        self.app_name, self.exch_config, self.recv_config = app_name, exch_config, recv_config
        self.exch_type, self.recv_type, self.format = exch_config['type'], recv_config['type'], recv_config['format']
        self.is_valid, self.id = False, f"{exch_config['uuid']}:{recv_config['uuid']}"
        self.reason = None
        
        self.formatO = FormatO(app_name, exch_config, recv_config)
        self.formatH = FormatH(app_name, exch_config, recv_config)
        self.formatE = FormatE(app_name, exch_config, recv_config)        

        self.parser = FormatBase.parser
        self.rootpath = self.__get_rootpath()


    def validation(self, data):
        try:
            if self.format == "old":
                self.is_valid, self.reason = self.formatO.validation(data)
            elif self.format == 'hana':
                self.is_valid, self.reason = self.formatH.validation(data)
            elif self.format == 'ext':
                self.is_valid, self.reason = self.formatE.validation(data)
            return self.is_valid, self.reason
        except Exception:
            return False, None


    def classify(self, data):
        try:
            if self.format == "old":
                config, class_name, logclass = self.formatO.classify(data)
            elif self.format == 'hana':
                config, class_name, logclass = self.formatH.classify(data)
            elif self.format == 'ext':
                config, class_name, logclass = self.formatE.classify(data)
 
            return config, class_name, logclass
        except Exception:
            return None, None


    def convert_csv(self, data):
        try:
            csv_data = None
            config, class_name, _ = self.classify(data)

            if config is None:
                return None

            data_list = [data[value['offset']:value['offset'] + value['length']]
                         for key, value in config.items()]

            csv_data = ','.join(map(str, data_list))
            return csv_data
        except Exception as e:
            log(self.app_name, f"Failed to convert data to CSV: {str(e)}")
            return None

    def __create_dir(self, dirname):
        try:
            if os.path.exists(dirname):
                return True

            path_parts = dirname.split(os.path.sep)
            current_path = "/"
            
            for part in path_parts:
                if not part:
                    continue

                current_path = os.path.join(current_path, part)

                if not os.path.exists(current_path):
                    os.makedirs(current_path)

            if os.path.exists(dirname):
                return True
            else:
                log(self.app_name, ERROR, f"Error creating directory {dirname}")
                return False
        except Exception as e:
            log(self.app_name, ERROR, f"Error creating directory {dirname}: {e}")
            return False

    def __get_rootpath(self):
        remote_hostname = self.exch_config['remote_hostname'].lower()
        exnm = self.exch_config['name']
        format = self.recv_config['format'].lower()
        ponm = self.recv_config['ponm']
        dirname = os.path.join(RAW_LOG_DIR, f"{remote_hostname}/{exnm}/{format}/{ponm}")        
        return dirname
    
    def __get_fullpath(self, logclass, data):
        current_hour = datetime.now().strftime("%H")
        filename = f"0{current_hour}.csv"
        
        # Join the filename with the rootpath and logclass
        fulldir = os.path.join(self.rootpath, logclass.lower())

        if not self.__create_dir(fulldir):
            return None
       
        fullpath = os.path.join(fulldir, filename)

        return fullpath
    
    def write_csv(self, data):
        _, _, logclass = self.classify(data)

        if logclass == 'DEPTH':
            try:
                if self.recv_config['depth_log'] == 0:
                    return
            except Exception:
                return


        fullpath = self.__get_fullpath(logclass, data)
        csv_data = self.convert_csv(data)

        try:
            modified_time = time.localtime(os.path.getmtime(fullpath))
            modified_yday = modified_time.tm_yday
        except FileNotFoundError:
            modified_yday = -1

        mode = 'a+' if datetime.now().timetuple().tm_yday == modified_yday else 'w+'
        
        with open(fullpath, mode, newline='', encoding='utf-8') as fd:
            fd.write(csv_data)
            fd.write("\n")
