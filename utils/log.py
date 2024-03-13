from utils.config import *
from utils.format import Format


def get_log_path(app_name):
    now = datetime.now()
    weekday = (now.weekday() + 1) % 7
    return os.path.join(LOG_DIR, f"{app_name}-{weekday}.log")

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

class Rawlog():
    def __init__(self, app_name, exch_config, recv_config):
        self.app_name, self.exch_config, self.recv_config = app_name, exch_config, recv_config
        self.id = f"{exch_config['uuid']}:{recv_config['uuid']}"
        self.rootpath = self.__get_rootpath()
        self.format = Format(app_name, exch_config, recv_config)

    def create_dir(self, dirname):
        try:
            if os.path.exists(dirname):
                return True

            path_parts = dirname.split(os.path.sep)
            current_path = ""
            
            for part in path_parts:
                current_path = os.path.join(current_path, part)
                if not os.path.exists(current_path):
                    os.makedirs(current_path)
            return True
        except Exception as e:
            print(f"Error creating directory {dirname}: {e}")
            return False

    def __get_rootpath(self):
        remote_hostname = self.exch_config['remote_hostname'].lower()
        exnm = self.exch_config['name'].lower()
        format = self.recv_config['format'].lower()
        ponm = self.recv_config['ponm'].lower()
        dirname = os.path.join(RAW_LOG_DIR, f"{remote_hostname}/{exnm}/{format}/{ponm}")
        
        if not self.create_dir(dirname):
            return None
        
        return dirname
    
    def __get_fullpath(self, logclass, data):
        current_hour = datetime.now().strftime("%H")
        filename = f"0{current_hour}.csv"
        
        # Join the filename with the rootpath and logclass
        fullpath = os.path.join(self.rootpath, logclass.lower(), filename)

        return fullpath
    
    def write_csv(self, data):
        _, _, logclass = self.format.classify(data)

        if logclass == 'DEPTH':
            try:
                if self.recv_config['depth_log'] == 0:
                    return
            except Exception:
                return


        fullpath = self.__get_fullpath(logclass, data)
        csv_data = self.format.convert_csv(data)

        try:
            modified_time = time.localtime(os.path.getmtime(fullpath))
            modified_yday = modified_time.tm_yday
        except FileNotFoundError:
            modified_yday = -1

        mode = 'a+' if datetime.now().timetuple().tm_yday == modified_yday else 'w+'
        
        with open(fullpath, mode, newline='', encoding='utf-8') as fd:
            fd.write(csv_data)
            fd.write("\n")


        
        
        
        