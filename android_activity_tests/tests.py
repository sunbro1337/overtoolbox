import subprocess
import time
import os
import random
from android_manipulation import unlock_device, kill_app, check_devices
from log import log


def lock_unlock(app, activity, iteration_of_test, iteration_of_rerun=1, sleep_of=0.01, sleep_to=0.05, phone_password=132465):
    """
    For low performance devices:
    Turn off animations on your test device — leaving system animations turned on in the test device might cause
    unexpected results or may lead your test to fail. Turn off animations from Settings by opening Developer options
    and turning all the following options off:
    -Window animation scale
    -Transition animation scale
    -Animator duration scale
    :param app: Ur app for test
    :param activity: Current activity for test
    :param iteration_of_rerun: Iteration of rerun test
    :param iteration_of_test: Iteration of test
    :param sleep_of: first arg for random.uniform, used for wait after unlock screen
    :param sleep_to: second arg for random.uniform, used for wait after unlock screen
    :param phone_password: phone password
    :return: void
    Key events:
    26 - Pressing the lock button
    82 - Unlock and ask for pin
    66 - Press ok on pin code screen
    """
    check_devices()
    for i in range(0, iteration_of_rerun):
        unlock_device(phone_password)
        time.sleep(0.01)
        kill_app(app)
        time.sleep(0.01)
        log(subprocess.getoutput(f"adb.exe shell am start -n {app}/{activity}"))
        time.sleep(0.01)
        log("Test progressing...")

        for j in range(0, iteration_of_test):
            sleep_time = random.uniform(sleep_of, sleep_to)
            unlock_device(phone_password)
            log(f"Sleep: {sleep_time}")
            time.sleep(sleep_time)
            os.system("adb.exe shell input keyevent 26")
        log("Done")



def suspend_resume(app, activity, iteration_of_test, time_sleep):
    """
    TODO If activity is not started before run test then test is broken and activity rerun with each new iteration
    :param app: Ur app for test
    :param activity: Current activity for test
    :param iteration_of_test: Iteration of test
    :param time_sleep: Time of sleep after resume/suspend
    :return: void
    Key events:
    3 - Press on home
    """
    log("Test progressing...")
    kill_app(app)
    for i in range(0, iteration_of_test):
        os.system("adb.exe shell input keyevent 3")
        time.sleep(time_sleep)
        log(subprocess.getoutput(f"adb.exe shell am start -n {app}/{activity}"))
        time.sleep(time_sleep)
    log("Done")
