import sys
import os
import select
import copy
import subprocess
import psutil
import signal
import atexit
import traceback
import ast
import threading
import time

from utils.log import log
from utils.config import (
    YELLOW, RED, GREEN, BLUE, WHITE, BOLD, RESET
)
from settings import (
    INSTALLED_APPS, PYTHON, EXIT_FLAG, 
    RUN_FLAG, END_FLAG, CHK_FLAG,
    MAIN_PIPE, MAIN_PIPE2, BASE_DIR,
    DEBUG, PROGRESS, ERROR, MUST
)
from utils.text import text_color

APP_NAME = "Main"
MAIN_RUN_FILE = "main.py"
TIMEOUT = 300
RUNNING_TABLE = []
MESSAGE_BUFFER = []
CURR_INSTALLED_APPS = {}

def create_named_pipe():
    try:
        if not os.path.exists(MAIN_PIPE):
            os.mkfifo(MAIN_PIPE)
        if not os.path.exists(MAIN_PIPE2):
            os.mkfifo(MAIN_PIPE2)
        log(APP_NAME, MUST, "{} and {} pipe successfully created".format(MAIN_PIPE, MAIN_PIPE2))
    except Exception as err:
        log(APP_NAME, ERROR, err)
        sys.exit()

def send_named_pipe(message):
    log(APP_NAME, MUST, "Send message now..")

    with open(MAIN_PIPE2, "w") as pipe:
        pipe.write(message)

def read_named_pipe(tnLock):
    try:
        global MESSAGE_BUFFER

        with open(MAIN_PIPE, 'r') as pipe:
            while True:
                data = None
                r, _, _ = select.select([pipe], [], [], TIMEOUT)

                try:
                    if r:
                        data = pipe.read()

                        if len(data) > 0:
                            log(APP_NAME, MUST, "Received request. Processing this now..")
                            log(APP_NAME, DEBUG, "Received Data : {}".format(data))

                            tnLock.acquire()
                            MESSAGE_BUFFER.append(data)
                            tnLock.release()
                except Exception as err:
                    log(APP_NAME, ERROR, err)

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def get_current_process_list():
    try:
        proc_list = []

        attrs = ['pid', 'name', 'cmdline', 'username']

        for process in psutil.process_iter(attrs):
            try:
                proc_info = process.as_dict(attrs=attrs)
                proc_list.append(proc_info)
            except Exception:
                continue
        
        return proc_list
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

# Create, Update
def run_process(app): 
    try:
        global RUNNING_TABLE

        for attr in RUNNING_TABLE:
            if attr['app_name'] == app:
                return
        
        app_path = os.path.join(BASE_DIR, app, MAIN_RUN_FILE)
        command_line = [PYTHON, app_path]

        log(APP_NAME, MUST, "Run the {} app now..".format(app))
        proc = subprocess.Popen(command_line, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        attr = {
                'app_name': app,
                'process': proc,
        }
        RUNNING_TABLE.append(attr)
    except Exception as err:
        log(APP_NAME, ERROR, err)

# Delete
def kill_process(app):
    try:
        global RUNNING_TABLE

        for attr in RUNNING_TABLE:
            if attr['app_name'] == app:
                log(APP_NAME, MUST, "Kill the {} app now..".format(app))
                attr['process'].kill()
                RUNNING_TABLE.remove(attr)
                break
    except Exception as err:
        log(APP_NAME, ERROR, err)

def run_all_process():
    try:
        global CURR_INSTALLED_APPS

        log(APP_NAME, MUST, "Run all of the process now..")

        for app, app_info in CURR_INSTALLED_APPS.items():
            if app_info['Running']:
                run_process(app)
        
    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def kill_all_process():
    try:
        global CURR_INSTALLED_APPS

        log(APP_NAME, MUST, "Kill all of the process now..")

        for app, app_info in CURR_INSTALLED_APPS.items():
            if app_info['Running']:
                kill_process(app)

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def check_all_process(send_flag=False):
    try:
        global CURR_INSTALLED_APPS
        global RUNNING_TABLE

        process_table = []
        proc_list = get_current_process_list()

        for app, app_info in CURR_INSTALLED_APPS.items():
            table = {
                'app_name': app,
                'state': '',
                'pid' : ''
            }
            find_app = False
            app_path = os.path.join(BASE_DIR, app, MAIN_RUN_FILE)
            cmd_line = [PYTHON, app_path]

            for proc in proc_list:
                if proc['cmdline'] == cmd_line:
                    find_app = True
                    table['state'] = text_color("Running", GREEN, True)
                    table['pid'] = proc.get('pid')
                    
                    if not app_info["Running"] and not send_flag:
                        kill_process(app)
                    break
            if not find_app:
                if app_info["Running"]:
                    table['state'] = text_color("Dead", RED, True)

                    if not send_flag:
                        run_process(app)
                else:
                    table['state'] = text_color("Off", YELLOW, True)

            process_table.append(table)
        
        if send_flag:
            send_named_pipe(str(process_table))

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()

def read_message_buffer(tnLock):
    try:
        global MESSAGE_BUFFER
        flag = None
        message = None
        
        if len(MESSAGE_BUFFER) > 0:
            tnLock.acquire()
            data = MESSAGE_BUFFER.pop(0)
            tnLock.release()

            if EXIT_FLAG in data:
                flag = EXIT_FLAG
            elif RUN_FLAG in data:
                flag = RUN_FLAG
                message = ast.literal_eval(data[len(RUN_FLAG):])
            elif CHK_FLAG in data:
                flag = CHK_FLAG

        return flag, message
    except Exception as err:
        log(APP_NAME, ERROR, err)

def exit_handler(signum, frame):
    try:
        log(APP_NAME, MUST, 'exit_handler() interrupt!')
        kill_all_process()
    except Exception as err:
        log(APP_NAME, ERROR, err)
    finally:
        sys.exit()

def exit_handler_wrapper():
    exit_handler(0, None)

def clean_zombie_process(signum, frame):
    global RUNNING_TABLE

    while True:
        try:
            # Wait for any terminated child processes
            pid, status = os.waitpid(-1, os.WNOHANG)
            
            if pid == 0:
                break  # No more child processes
            
            for attr in RUNNING_TABLE:
                if attr['process'].pid == pid:
                    proc_name = attr['app_name']
                    log(APP_NAME, MUST, "'{}' process aborted.".format(proc_name))
                    RUNNING_TABLE.remove(attr)
                    break

        except ChildProcessError:
            break

def runserver():
    try:
        global CURR_INSTALLED_APPS
        IS_RUNNING = True

        log(APP_NAME, MUST, "Main server start..!")

        CURR_INSTALLED_APPS = copy.deepcopy(INSTALLED_APPS)

        create_named_pipe()

        run_all_process()

        atexit.register(exit_handler_wrapper)
        signal.signal(signal.SIGTERM, exit_handler)
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        signal.signal(signal.SIGINT, exit_handler)
        signal.signal(signal.SIGCHLD, clean_zombie_process)

        tnLock = threading.Lock()

        tn = threading.Thread(target=read_named_pipe, args=(tnLock, ))
        tn.start()

        while True:
            if IS_RUNNING:
                check_all_process()

            flag, message = read_message_buffer(tnLock)

            if flag == RUN_FLAG:
                IS_RUNNING = True
                new_installed_apps = message
                
                for new_app, new_info in new_installed_apps.items():
                    if new_app in CURR_INSTALLED_APPS:
                        if new_app == "Main":
                            continue
                        curr_info = CURR_INSTALLED_APPS[new_app]

                        if new_info['Running'] != curr_info["Running"]:
                            if new_info['Running']:
                                run_process(new_app)
                            else:
                                kill_process(new_app)
                    else:
                        if new_info["Running"]:
                            run_process(new_app)
                            
                CURR_INSTALLED_APPS = copy.deepcopy(new_installed_apps)     
                send_named_pipe(END_FLAG)          
            elif flag == EXIT_FLAG:
                IS_RUNNING = False
                kill_all_process()
                send_named_pipe(END_FLAG)
            elif flag == CHK_FLAG:
                check_all_process(send_flag=True)

    except Exception as err:
        traceback_error = traceback.format_exc()
        log(APP_NAME, ERROR, traceback_error)
        sys.exit()