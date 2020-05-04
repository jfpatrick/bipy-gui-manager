from typing import Any, Optional, Tuple
import os
import shutil
from bipy_gui_manager import cli_utils as cli
from bipy_gui_manager.phonebook.phonebook import Phonebook, PhonebookEntry


def validate_or_fail(value, validator, neg_feedback):
    """ Either return the value if valid, or throw ValueError """
    if value is None or not validator(value):
        raise ValueError(neg_feedback)
    return value


def validate_or_ask(validator, question, neg_feedback, start_value=None, pos_feedback=None, hints=()):
    """ Either return start_value if valid, or ask the user until they give a valid value """
    value = start_value
    while value is None or not validator(value):
        if value:
            cli.negative_feedback(neg_feedback)
            for hint in hints:
                cli.give_hint(hint)
        value = cli.ask_input(question)
    if pos_feedback:
        cli.positive_feedback(pos_feedback.format(value))
    return value


# def validate_as_arg_or_ask(cli_value, validator, question, neg_feedback, pos_feedback=None, hints=(), interactive=True)\
#         -> bool:
#     """
#         If an initial value is given and valid, return it.
#         If an initial value is given and invalid, fail.
#         If it's not given, ask the user until a valid value is received.
#         if interactive is False, fail rather than asking.
#     """
#     if not interactive and cli_value is None:
#         raise ValueError(neg_feedback)
#     if cli_value is not None or not interactive:
#         result = validate_or_fail(cli_value, validator, neg_feedback)
#         if pos_feedback:
#             cli.positive_feedback(pos_feedback.format(result))
#         return result
#     else:
#         return validate_or_ask(validator, question, neg_feedback, pos_feedback=pos_feedback, hints=hints)


def resolve_as_arg_or_ask(initial_value, resolver, question, neg_feedback, pos_feedback=None, hints=(),
                          interactive=True) -> Any:
    """
        If an initial value is given and valid, resolve and return it.
        If an initial value is given and invalid, fail.
        If it's not given, ask the user until a valid value is received and return it's resolved version.
        if interactive is False, fail rather than asking.
    """
    # Can't ask for a new value if what's given is wrong
    if not interactive:

        # Either it's valid or I fail
        value, success = resolver(initial_value)
        if not success:
            raise ValueError(neg_feedback)
        if pos_feedback:
            cli.positive_feedback(pos_feedback.format(value))
        return value

    else:
        # Either it's valid or I ask
        value, success = resolver(initial_value)

        while not success:
            value = cli.ask_input(question)
            value, success = resolver(value)
            if not success:
                cli.negative_feedback(neg_feedback)
                for hint in hints:
                    cli.give_hint(hint)
            else:
                if pos_feedback:
                    cli.positive_feedback(pos_feedback.format(value))
                return value

        return value


def validate_base_path(base_path: str, project_name: str, interactive: bool = True, overwrite: bool = False) \
        -> Tuple[Optional[str], bool]:
    """
    Makes sure there is no folder with the name of the new project and if so ask the user and act accordingly.
    :param base_path: path to the new project
    :param project_name: name of the folder for the new project
    :param interactive: whether the use should be asked what to do if the path exist
    :param overwrite: whether to automatically overwrite the existing folder
    :return True if the path is available
    """
    if base_path is None:
        return None, False

    project_path = os.path.join(base_path, project_name)
    if os.path.exists(project_path):
        if overwrite:
            cli.list_subtask("Overwriting folder {}".format(project_path))
            shutil.rmtree(project_path)
            return base_path, True
        elif not interactive:
            raise OSError("Directory '{}' already exists.".format(project_path))
        else:
            answer = cli.handle_failure("A folder called '{}' already exists. ".format(project_path) +
                                        "Do you want to overwrite it or to enter another path? (overwrite/another)")
            if answer == "overwrite":
                cli.list_subtask("Overwriting existing folder")
                shutil.rmtree(project_path)
                return base_path, True
            return None, False
    return base_path, True


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


def validate_gitlab(gitlab, repo_type, upload_protocol, clone_protocol, project_name, cern_id) -> Optional[str]:
    """
    Ensures all the parameters related to GitLab are in order.
    :return: a dictionary containing the 'gitlab' and 'repo_url' values
    """
    if gitlab:
        # Make sure the upload protocol is specified
        if upload_protocol is None:
            upload_protocol = clone_protocol

        if repo_type == 'operational':
            group = "bisw-python"
        elif repo_type == 'test':
            group = cern_id
        else:
            raise ValueError("Repository type not recognized: '{}'".format(repo_type))

        if upload_protocol == 'ssh':
            repo_url = "ssh://git@gitlab.cern.ch:7999/{}/{}.git".format(group, project_name)
        elif upload_protocol == 'https':
            repo_url = "https://gitlab.cern.ch/{}/{}.git".format(group, project_name)
        elif upload_protocol == 'kerberos':
            repo_url = "https://:@gitlab.cern.ch:8443/{}/{}.git".format(group, project_name)
        else:
            raise ValueError("Upload protocol not recognized: '{}'".format(upload_protocol))
    else:
        repo_url = None

    return repo_url


def validate_cern_id(cern_id: str) -> Tuple[Optional[PhonebookEntry], bool]:
    """
    Uses the Phonebook utilities to validate CERN IDs and retrieve their data.
    :param cern_id: The CERN ID of the user
    :return: A PhonebookEntry object containing all the user's info
    """
    phonebook = Phonebook(cern_id)
    entries = phonebook.query_data()
    print(entries)
    if len(entries) == 1 and cern_id in [login.cern_id for login in entries[0].login_list]:
        return entries[0], True
    return None, False
