# TODO manage better those ANSI Color code escapes

def draw_line():
    print("_________________________________________________________________________")

def ask_input(string):
    return input("\033[0;32m=>\033[0;m {}  ".format(string))

def handle_failure(string):
    return input("\033[0;31m=> Error!\033[0;33m {}  \033[0;m".format(string))

def positive_feedback(string):
    print("\033[0;32m=>\033[0;m {}  ".format(string))

def success_feedback():
    print("   \033[0;32mDone\033[0;m ")

def give_hint(string):
    print("    - Hint: {}".format(string))

def negative_feedback(string):
    print("\033[0;31m=> Error!\033[0;33m {}\033[0;m".format(string))
