from tabulate import tabulate

import argparse
import sys
import ast
import os

from settings import (
    INSTALLED_APPS,
    RUN_FLAG, END_FLAG, EXIT_FLAG, CHK_FLAG,
    MAIN_PIPE, MAIN_PIPE2
)

from runserver import (
    runserver
)

def send_request(message):
    try:
        if not os.path.exists(MAIN_PIPE):
            raise Exception("Main server is not running now. Please run 'python3 manage.py runserver'.")

        with open(MAIN_PIPE, "w") as pipe:
            pipe.write(message)

    except Exception as err:
        print(err)
        sys.exit()

def read_request():
    try:
        if not os.path.exists(MAIN_PIPE2):
            raise Exception("Main server is not running now. Please run 'python3 manage.py runserver'.")

        with open(MAIN_PIPE2, "r") as pipe:
            flag = pipe.read()

            return flag
    except Exception as err:
        print(err)
        sys.exit()

def run():
    message = RUN_FLAG + str(INSTALLED_APPS)
    send_request(message)

    while True:
        flag = read_request()

        if flag == END_FLAG:
            break

    print("Request successfully done.")

def killall():
    send_request(EXIT_FLAG)

    while True:
        flag = read_request()

        if flag == END_FLAG:
            break

    print("Request successfully done.")

def print_table(table):
    try:
        headers = table[0].keys()
        rows = [list(row.values()) for row in table]
        table_output = tabulate(rows, headers=headers, tablefmt="fancy_grid")
        print(table_output)
    except Exception as err:
        print(err)
        sys.exit()

def runcheck():
    send_request(CHK_FLAG)

    while True:
        message = read_request()

        if len(message) > 0:
            data = ast.literal_eval(message)
            print_table(data)
            break


def main():
    parser = argparse.ArgumentParser(prog="python3 manage.py", description="Management script of the SDMS(Stock Data Monitoring System) program")
    subparsers = parser.add_subparsers(title="commands", dest="command", metavar="command")

    # Runserver command
    runserver_parser = subparsers.add_parser("runserver", help="Execute the main server (run in the background)")

    # Run command
    run_parser = subparsers.add_parser("run", help="Query the running signal to the main server")

    # Check the running process command
    check_parser = subparsers.add_parser("runcheck", help="Check what process is running now")

    # Exit command
    exit_parser = subparsers.add_parser("killall", help="Send the exit signal to the main server")

    args = parser.parse_args()

    if args.command == "runserver":
        runserver()
    elif args.command == "run":
        run()
    elif args.command == "killall":
        killall()
    elif args.command == "runcheck":
        runcheck()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()