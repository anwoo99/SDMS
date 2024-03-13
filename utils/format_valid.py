from utils.config import *


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
