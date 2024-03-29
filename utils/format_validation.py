from utils.config import *
from utils.log import log

def parser(config, data, field_name: str):
        if config is None:
            return None

        try:
            start, end = config[field_name]['offset'], config[field_name]['offset'] + config[field_name]['length']
            return data[start:end]
        except Exception:
            return None


def formatO_validation(config, class_name, data):
    """
    필요한 valdiation을 기입하세요. 
    """

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

        return True, None
    except Exception as err:
        return False, "Failed to validation for formatO"


def formatH_validation(config, class_name, data):
    """
    필요한 valdiation을 기입하세요. 
    Return은 반드시 (is_valid(boolean), reason(str)) 으로 작성하세요.
    """

    try:
        if class_name is None or config is None:
            return False, "Unknown data type"

        if class_name == 'HANA_FUTURE_M':
            pass
        elif class_name == 'HANA_OPTION_M':
            pass
        elif class_name == 'HANA_FUTURE_QUOTE':
            pass
        elif class_name == 'HANA_OPTION_QUOTE':
            pass
        elif class_name == 'HANA_FUTURE_DEPTH':
            pass
        elif class_name == 'HANA_OPTION_DEPTH':
            pass
        elif class_name == 'HANA_FUTURE_SETTLE':
            pass
        elif class_name == 'HANA_OPTION_SETTLE':
            pass

        return True, None
    except Exception as err:
        return False, "Failed to validation for formatH"


def formatE_validation(config, class_name, data):
    """
    필요한 valdiation을 기입하세요. 
    Return은 반드시 (is_valid(boolean), reason(str)) 으로 작성하세요.
    """

    try:
        if class_name is None or config is None:
            return False, "Unknown data type"

        if class_name == 'EXT_FUTURE_M':
            pass
        elif class_name == 'EXT_OPTION_M':
            pass
        elif class_name == 'EXT_SPREAD_M':
            pass
        elif class_name == 'EXT_TRADE':
            pass
        elif class_name == 'EXT_SETTLE':
            pass
        elif class_name == 'EXT_CLOSE':
            pass
        elif class_name == 'EXT_OINT':
            pass
        elif class_name == 'EXT_DEPTH':
            pass

        return True, None
    except Exception as err:
        return False, "Failed to validation for formatE"

