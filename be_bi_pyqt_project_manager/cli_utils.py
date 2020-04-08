# TODO manage better those ANSI Color code escapes

def positive_feedback(string):
    return "\033[0;32m=>\033[0;m {}  ".format(string)

def success_feedback():
    return "   \033[0;32mDone\033[0;m "

def give_hint(string):
    return "    - Hint: {}".format(string)

def negative_feedback(string):
    return "\033[0;31m=> Error!\033[0;33m {}\033[0;m".format(string)
