"""
Pyinstaller rules
pyinstaller.exe main.py -n "mobile_svn_rebase" --add-binary ".;svn_rebase.exe" --add-binary ".;svn_rebase_prepare.exe" --onefile
"""
import datetime
import os
import argparse
import subprocess
import sys
import time
from shutil import rmtree

import txts
import styles


SVN_REBASE_EXE = f'py.exe -2.7 {os.path.join("D:", "Source", "tools", "svn_rebase.py")}'
SVN_REBASE_PREPARE_EXE = f'py.exe -2.7 {os.path.join("D:", "Source", "tools", "svn_rebase_prepare.py")}'


def find_working_branch(cwd):
    for line in subprocess.getoutput(f"svn info {cwd}").split("\n"):
        if "Relative URL" in line:
            return line.replace("Relative URL: ^", "")


def open_edit(editor_path, file_path):
    print(f"\nEdit {REBASE_DATA_PATH}")
    print(styles.warning(txts.EDIT_FILE))
    print(styles.success("Editing..."))
    editor_status = subprocess.getoutput(f"{editor_path} {file_path}")
    if "is not recognized as an internal or external command" in editor_status:
        print(f"{EDITOR_PATH} not found, add {editor_path} in PATH(install if u don't have it) and reload session")
        return 1
    else:
        print("File rebase.data is closed")
        return 0


def rebase(rebase_data_path, cwd=None):
    print(styles.success("Rebase is processing..."))
    if cwd:
        os.system(f"cd {cwd} & {SVN_REBASE_EXE} {rebase_data_path}")
    else:
        os.system(f"{SVN_REBASE_EXE} {rebase_data_path}")
    print("Done")


def rebase_continue(cwd=None):
    print(styles.success("Rebase is continuing..."))
    if cwd:
        os.system(f"cd {cwd} & {SVN_REBASE_EXE} --continue")
    else:
        os.system(f"{SVN_REBASE_EXE} --continue")
    print("Done")


def rebase_data_generate(branch_for_rebase, branch_to_rebase, rebase_data_path):
    print(f"\nGenerate a rebase.data file that stored in {rebase_data_path}")
    print(branch_for_rebase)
    os.system(f"cd {args.cwd} && {SVN_REBASE_PREPARE_EXE} {branch_for_rebase} --upstream {branch_to_rebase} -o {rebase_data_path} --cwd {args.cwd}")


def rebase_approve():
    while True:
        user_input = input(styles.warning(txts.REBASE_APPROVE))
        if user_input == "Y" or user_input == "y":
            return 0
        elif user_input == "N" or user_input == "n":
            return 1
        else:
            return 2


def rebase_data_check_file(file):
    rebase_data = open(file, "r")
    for line in rebase_data:
        for i in DEFAULT_EXCEPTIONS:
            if i in line:
                rebase_data.close()
                return False
    rebase_data.close()
    return True


def rebase_data_check(rebase_data_path, exceptions_path):
    check_file_with_exceptions(exceptions_path)
    check_approve = rebase_data_check_file(rebase_data_path)
    while check_approve is False:
        print(styles.error(txts.REBASE_ERROR_COMMITS))
        open_edit(EDITOR_PATH, rebase_data_path)
        check_file_with_exceptions(exceptions_path)
        check_approve = rebase_data_check_file(rebase_data_path)


def check_snv_rebase_dir(cwd):
    svn_rebase_dir = f"{cwd}\\.svn_rebase"
    if os.path.exists(svn_rebase_dir):
        user_input = input(styles.warning(txts.SVN_REBASE_ALREADY_EXIST))
        if user_input == "Y" or user_input == "y":
            return 0
        elif user_input == "N" or user_input == "n":
            rmtree(svn_rebase_dir)
            return 1
        else:
            return 2
    else:
        return 1


def read_file(file):
    file = open(file)
    str_list = file.readlines()
    file.close()
    return str_list


def create_file_with_exceptions(exceptions_path):
    if os.path.exists(exceptions_path):
        print(f"\nFile with exceptions is recognize in {exceptions_path}")
        return 1
    else:
        print(f"\nCreate file with exceptions that stored in {exceptions_path}")
        file = open(exceptions_path, "w")
        for i in DEFAULT_EXCEPTIONS:
            file.write(f"{i}\n")
        file.close()
        print(f"File {exceptions_path} created")
        return 0


def check_file_with_exceptions(exceptions_path):
    if os.path.exists(exceptions_path):
        exceptions = read_file(exceptions_path)
        for ex_line in exceptions:
            rebase_data_lines = read_file(REBASE_DATA_PATH)
            rebase_data_result = open(REBASE_DATA_PATH, "w")
            for line in rebase_data_lines:
                if ex_line not in line:
                    rebase_data_result.write(line)
            rebase_data_result.close()


if __name__ == "__main__":
    EDITOR_PATH = 'notepad.exe'
    BRANCH_TO_REBASE = '"console/main"'

    parser = argparse.ArgumentParser(prog="svn_rebase")
    parser.add_argument("cwd",
                        metavar="branch_dir",
                        help="Work branch directory")
    parser.add_argument("-b", "--branch",
                        help="Branch that needed to rebase",
                        type=str)
    parser.add_argument("-u", "--upstream",
                        help="Branch for upstream",
                        type=str,
                        default=BRANCH_TO_REBASE)
    parser.add_argument('--continue',
                        help='Continue an interrupted rebase process',
                        action='store_true')
    args = parser.parse_args()

    if args.branch:
        BRANCH_FOR_REBASE = f'"{args.branch}"'
    else:
        BRANCH_FOR_REBASE = f'"{find_working_branch(args.cwd)}"'
    DATETIME_NOW = f'{datetime.datetime.now().date()}_{datetime.datetime.now().strftime("%H_%M_%S")}'
    REBASE_DATA_ROOT_PATH = os.path.join(args.cwd, '.svn', 'rebase_data', f'{DATETIME_NOW}')
    if not os.path.exists(REBASE_DATA_ROOT_PATH):
        os.makedirs(REBASE_DATA_ROOT_PATH)
    REBASE_DATA_PATH = os.path.join(REBASE_DATA_ROOT_PATH, 'rebase.data')
    EXCEPTIONS_PATH = os.path.join(REBASE_DATA_ROOT_PATH, 'rebase_data_trash.txt')
    DEFAULT_EXCEPTIONS = ['job-spb-dp-svn', '"Remove the branch for rebasing"']

    print(args)
    print(f"Current working directory: {args.cwd}")
    print(f"Actual editor: {EDITOR_PATH}")
    print(f"Rebase {BRANCH_FOR_REBASE} to {args.upstream}")

    if getattr(args, 'continue', True):
        if args.cwd == ".":
            rebase_continue()
        else:
            rebase_continue(args.cwd)
        input(styles.success("\nPress Enter to close..."))
    elif check_snv_rebase_dir(args.cwd) == 2:
        input(styles.success("\nPress Enter to close..."))
    elif check_snv_rebase_dir(args.cwd) == 0:
        if args.cwd == ".":
            rebase_continue()
        else:
            rebase_continue(args.cwd)
        input(styles.success("\nPress Enter to close..."))
    elif check_snv_rebase_dir(args.cwd) == 1:
        create_file_with_exceptions(EXCEPTIONS_PATH)
        rebase_data_generate(BRANCH_FOR_REBASE, args.upstream, REBASE_DATA_PATH)
        rebase_data_check(REBASE_DATA_PATH, EXCEPTIONS_PATH)
        open_edit_status = open_edit(EDITOR_PATH, REBASE_DATA_PATH)
        rebase_data_check(REBASE_DATA_PATH, EXCEPTIONS_PATH)
        if open_edit_status == 1:
            sys.exit()
        approve = rebase_approve()
        while approve == 1:
            open_edit(EDITOR_PATH, REBASE_DATA_PATH)
            approve = rebase_approve()
        if approve == 0:
            if args.cwd == ".":
                rebase(REBASE_DATA_PATH)
            else:
                rebase(REBASE_DATA_PATH, args.cwd)
            input(styles.success("\nPress Enter to close..."))
        elif approve == 2:
            print('Rebase is terminated')
            input(styles.success("\nPress Enter to close..."))
