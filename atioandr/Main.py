"""
---Pyinstaller rules---
pyinstaller Main.py -n "aitoandr" --onefile
"""
import argparse
import datetime
import os
import subprocess
import sys
# import time

from tqdm import tqdm

def deviceDefinition():
    return os.system('adb.exe devices')


def appInstall(packagePath):
    print('Install Legends')
    logFile = open("install_apk.log", "w")
    # TODO
    # adb shell appops set --uid com.lesta.legends.hybrid MANAGE_EXTERNAL_STORAGE - need to implement for 11 andr,
    # android.permission.WRITE_EXTERNAL_STORAGE and android.permission.READ_EXTERNAL_STORAGE for 10 andr
    for apk in tqdm(packagePath):
        logFile.write(str(datetime.datetime.now()) + subprocess.getoutput(f'adb.exe install -r -g "{apk}"') + '\n')
    logFile.close()


def clearPackageData():
    if sys.platform == "win32":
        apks = subprocess.getoutput("adb.exe shell pm list packages | findstr com.lesta.legends")
    else:
        apks = subprocess.getoutput("adb.exe shell pm list packages | grep com.lesta.legends")
    print(f"Already installed apks:\n{apks}")
    print("Clear data")
    packages = ["com.lesta.legends.hybrid", "com.lesta.legends.perf", "com.lesta.legends"]
    for package in tqdm(packages):
        subprocess.getoutput(f"adb.exe uninstall {package}")
    # os.system("adb.exe shell rm -r /sdcard/wows_content")
    os.system("adb.exe shell rm -r /sdcard/wowsc")


def sendGameRes(resourcesPath):
    print('Create dir wows_content')
    os.system("adb.exe shell mkdir /sdcard/wows_content")
    print('Install resources')
    logFile = open("install_res.log", "w")
    for file in tqdm(os.listdir(f"{resourcesPath}")):
        logFile.write(str(datetime.datetime.now())
                      + subprocess.getoutput(f'adb.exe push "{resourcesPath}\{file}" /sdcard/wows_content') + '\n')
    logFile.close()


def senGameConfig(configPath):
    print('Create dir wowsc')
    os.system("adb.exe shell mkdir /sdcard/wowsc")
    print('Install config')
    logFile = open("install_conf.log", "w")
    for i in tqdm(configPath):
        logFile.write(str(datetime.datetime.now()) + subprocess.getoutput(f'adb.exe push "{i}" /sdcard/wowsc') + '\n')
    logFile.close()


def getVersion():
    packages = ["com.lesta.legends.hybrid", "com.lesta.legends.perf", "com.lesta.legends"]
    for package in packages:
        print(f"\n{package}:")
        os.system(f"adb.exe shell dumpsys package {package} | grep version")
        print("\n")


if __name__ == "__main__":
    print("AiToAndr v1.1")

    parser = argparse.ArgumentParser(prog="aitoanrd")
    parser.add_argument("-p", "--package", nargs="+", help="Path to a legends apks", type=str)
    parser.add_argument("-r", "--resources", help="Path to a dir with resources for legends", type=str)
    parser.add_argument("-c", "--config", nargs="+", help="Path to ur config for legends", type=str)
    args = parser.parse_args()

    deviceDefinition()
    getVersion()
    if args.package:
        clearPackageData()
        appInstall(args.package)
    if args.resources:
        sendGameRes(args.resources)
    if args.config:
        senGameConfig(args.config)
    os.system("adb.exe kill-server")
    sys.exit()
