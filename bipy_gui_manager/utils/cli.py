# TODO manage better those ANSI Color code escapes


def print_welcome():
    print("_________________________________________________________________________\n")
    print("  Welcome to BI's PyQt5 Project Setup Wizard!")
    print("_________________________________________________________________________\n")


def draw_line():
    print("\n_________________________________________________________________________\n")


def ask_input(string):
    return input("\033[0;33m=>\033[0;m {}  ".format(string))


def handle_failure(string):
    return input("\033[0;31m=> Error!\033[0;33m {} \033[0;m".format(string))


def positive_feedback(string, newline=True):
    if newline:
        print("\033[0;32m=>\033[0;m {}\n".format(string))
    else:
        print("\033[0;32m=>\033[0;m {}  ".format(string))


def list_subtask(string):
    print("    - {}".format(string))


def give_hint(string):
    print("    - Hint: {}".format(string))


def negative_feedback(string):
    print("\033[0;31m=> Error!\033[0;33m {}\033[0;m".format(string))
