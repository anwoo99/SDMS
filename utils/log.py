from config import *

def log(app_name, level, content):
    if app_name is None:
        print(content)
        return

    if LOG_LEVEL_MAP[level] < LOG_LEVEL_MAP[INSTALLED_APPS[app_name]["LOG_LEVEL"]]:
        return

    caller = inspect.currentframe().f_back
    caller_function = inspect.getframeinfo(caller).function
    now = datetime.now()
    yday = now.timetuple().tm_yday
    weekday = (now.weekday() + 1) % 7
    log_path = "{}/{}-{}.log".format(LOG_DIR, app_name, weekday)
    date_head = now.strftime("%m/%d %H:%M:%S")

    try:
        modified_time = time.localtime(os.path.getmtime(log_path))
        modified_yday = modified_time.tm_yday
    except:
        modified_yday = -1

    mode = 'a+'

    if yday != modified_yday:
        mode = 'w+'

    logmsg = "[{}] [{}] {}\n".format(date_head, caller_function, content)

    with open(log_path, mode) as fd:
        fd.write(logmsg)
