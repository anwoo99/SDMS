from utils.config import *

def get_log_path(app_name):
    now = datetime.now()
    weekday = (now.weekday() + 1) % 7
    sys_path = os.path.join(LOG_DIR, "sys")

    if not os.path.exists(sys_path):
        os.makedirs(sys_path)

    return os.path.join(sys_path, f"{app_name}-{weekday}.log")

def should_log(app_name, level):
    if app_name is None:
        return True

    try:
        log_level = LOG_LEVEL_MAP[INSTALLED_APPS[app_name]["LOG_LEVEL"]]
    except KeyError:
        return app_name == "Main"

    return LOG_LEVEL_MAP[level] >= log_level

def log(app_name, level, content):
    if not should_log(app_name, level):
        return

    caller = inspect.currentframe().f_back
    caller_function = inspect.getframeinfo(caller).function
    log_path = get_log_path(app_name)
    date_head = datetime.now().strftime("%m/%d %H:%M:%S")

    try:
        modified_time = time.localtime(os.path.getmtime(log_path))
        modified_yday = modified_time.tm_yday
    except FileNotFoundError:
        modified_yday = -1

    mode = 'a+' if datetime.now().timetuple().tm_yday == modified_yday else 'w+'

    logmsg = f"[{date_head}] [{caller_function}] {content}\n"

    with open(log_path, mode) as fd:
        fd.write(logmsg)

def get_errlog_path(error_code):
    now = datetime.now()
    weekday = (now.weekday() + 1) % 7
    err_path = os.path.join(LOG_DIR, "err")

    if not os.path.exists(err_path):
        os.makedirs(err_path)

    return os.path.join(err_path, f"{error_code}-{weekday}.log")

def errlog(data):
    if "error_code" not in data:
        return

    content = ', '.join([f"{key}: {value}" for key, value in data.items()])
    log_path = get_errlog_path(data["error_code"])
    date_head = datetime.now().strftime("%m/%d %H:%M:%S")

    try:
        modified_time = time.localtime(os.path.getmtime(log_path))
        modified_yday = modified_time.tm_yday
    except FileNotFoundError:
        modified_yday = -1

    mode = 'a+' if datetime.now().timetuple().tm_yday == modified_yday else 'w+'

    logmsg = f"[{date_head}] {content}\n"

    with open(log_path, mode) as fd:
        fd.write(logmsg)
        
        
        