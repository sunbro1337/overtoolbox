class Colors:
    pref = "\033["
    reset = f"{pref}0m"
    black = "30m"
    red = "31m"
    green = "32m"
    yellow = "33m"
    blue = "34m"
    magenta = "35m"
    cyan = "36m"
    white = "37m"
    italics = "3m"


def italics(txt):
    return  f"{Colors.pref}{Colors.italics}{txt}{Colors.reset}"


def warning(txt):
    return f"{Colors.pref}{Colors.yellow}{txt}{Colors.reset}"


def error(txt):
    return f"{Colors.pref}{Colors.red}{txt}{Colors.reset}"


def success(txt):
    return f"{Colors.pref}{Colors.green}{txt}{Colors.reset}"
