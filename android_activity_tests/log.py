import datetime
from constants import LogLvl


def log(message, log_lvl=LogLvl.INFO):
    print(f"{datetime.datetime.now()} {log_lvl}: {message}")

