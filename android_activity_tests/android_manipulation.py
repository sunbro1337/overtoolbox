import os
import subprocess
import sys
import time
from log import log
from constants import LogLvl


def check_devices():
    check = subprocess.getoutput("adb.exe shell ls")
    if "no devices/emulators found" in check:
        log("adb.exe: no devices/emulators found", LogLvl.WARNING)
        sys.exit()
    elif "more than one device/emulator" in check:
        log("error: more than one device and emulator", LogLvl.WARNING)
        sys.exit()


def current_device(device):
    # TODO
    os.system(f"adb.exe -s {device} shell ls")


def unlock_device(phone_password):
    log("Unlocking device...")
    os.system("adb.exe shell input keyevent 26")
    time.sleep(0.01)
    os.system("adb.exe shell input touchscreen swipe 930 880 930 380")  # Swipe up for xiaomi, huawey
    # os.system("adb shell input keyevent 82") # use for samsung
    time.sleep(0.01)
    os.system(f"adb.exe shell input text {phone_password}")  # input text
    # os.system("adb.exe shell input keyevent 66") # use for samsung
    log("Device unlocked")


def kill_app(app):
    log("Killing app...")
    os.system(f"adb.exe shell am force-stop {app}")
    time.sleep(0.01)
    os.system(f"adb.exe shell am kill {app}")
    log(f"App {app} killed")
