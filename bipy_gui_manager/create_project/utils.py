import os
from subprocess import Popen, PIPE
from bipy_gui_manager import cli_utils as cli


def invoke_git(parameters=(), cwd=os.getcwd(), allow_retry=False, neg_feedback="An error occurred in Git!"):
    """
    Perform a syscall to the local Git executable
    :param parameters: parameters to pass to Git, as an array
    :param cwd: working directory for Git
    :param allow_retry: on fail, let the user decide if they want to retry or not
    :param neg_feedback: message to explain a potential failure
    :return: Nothing if the command succeeds, OSError if it fails
    """
    command = ['/usr/bin/git']
    command.extend(parameters)

    while True:
        git_query = Popen(command, cwd=cwd, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = git_query.communicate()

        if git_query.poll() == 0:
            return
        else:
            cli.negative_feedback(stderr.decode('utf-8'))

            if not allow_retry:
                raise OSError(neg_feedback)

            answer = cli.handle_failure("Do you want to retry? (yes/no)")
            if answer == "no" or answer == "n":
                raise OSError(neg_feedback)


def validate_or_fail(value, validator, neg_feedback):
    """ Either return the value if valid, or throw ValueError """
    try:
        if validator(value):
            return value
    except Exception as e:
        raise ValueError("Unexpected validation exception: {}".format(e))
    raise ValueError(neg_feedback)


def validate_or_ask(validator, question, neg_feedback, start_value="", pos_feedback=None, hints=()):
    """ Either return start_value if valid, or ask the user until they give a valid value """
    value = start_value
    while not validator(value):
        if value != "":
            cli.negative_feedback(neg_feedback)
            for hint in hints:
                cli.give_hint(hint)
        value = cli.ask_input(question)
    if pos_feedback:
        cli.positive_feedback(pos_feedback.format(value))
    return value


def validate_as_arg_or_ask(cli_value, validator, question, neg_feedback, pos_feedback=None, hints=(), interactive=True):
    """
        If an initial value is given and valid, return it.
        If an initial value is given and invalid, fail.
        If it's not given, ask the user until a valid value is received.
        if interactive is False, fail rather than asking.
    """
    if not interactive and cli_value is None:
        raise ValueError(neg_feedback)
    if (cli_value and cli_value != "") or not interactive:
        result = validate_or_fail(cli_value, validator, neg_feedback)
        if pos_feedback:
            cli.positive_feedback(pos_feedback.format(result))
        return result
    else:
        return validate_or_ask(validator, question, neg_feedback, pos_feedback=pos_feedback, hints=hints)


def validate_demo_flags(force_demo: bool, demo: bool, interactive: bool) -> bool:
    """
    Checks which combination of values are contained in the parameters and returns the correct value
    for parameters.demo, eventually asking the user if necessary
    :param force_demo: whether the --with-demo flag was passed
    :param demo: opposite of whether the --no-demo flag was passed
    :param interactive: whether the script overall is allowed to ask anything to the user interactively
    :return: True if demo should be included, False otherwise
    """
    if force_demo and demo:
        # --with-demo was passed
        cli.positive_feedback("Your project will contain a demo application.")
        return True
    elif not force_demo and not demo:
        # only --no-demo was passed
        cli.positive_feedback("Your project will not contain the demo application.")
        return False
    elif not force_demo and demo and not interactive:
        # Neither --with-demo nor --no-demo were passed, but --not-interactive was specified: default to yes
        cli.positive_feedback("Your project will contain a demo application.")
        return True
    elif not force_demo and demo:
        # Neither --with-demo nor --no-demo were passed, but --not-interactive was specified
        value = cli.ask_input("Do you want to install a \033[0;33mdemo application\033[0;m within your project? "
                              "It's especially recommended to beginners (yes/no)")
        while True:
            if value == "n" or value == "no":
                cli.positive_feedback("Your project will \033[0;33mnot contain the demo application\033[0;m.")
                return False
            elif value == "y" or value == "yes":
                cli.positive_feedback("Your project will \033[0;32mcontain a demo application\033[0;m.")
                return True
            else:
                value = cli.handle_failure("Please type yes or no:")
