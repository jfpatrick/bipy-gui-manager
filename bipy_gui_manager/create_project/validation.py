from typing import Any, Optional, Tuple
import os
import shutil
from pyphonebook import PhoneBook, PhoneBookEntry
from bipy_gui_manager import cli_utils as cli
from bipy_gui_manager.create_project.constants import GROUP_NAME


def resolve_as_arg_or_ask(initial_value, resolver, question, neg_feedback, hints=(),
                          interactive=True) -> Any:
    """
        if not interactive resolve and either succeed or fail
        If interactive, resolve and either succeed or ask again
    """
    if not interactive:

        # Either it's valid or I fail
        value, success = resolver(initial_value)
        if not success:
            raise ValueError(neg_feedback)
        return value

    else:
        # Either it's valid or I ask
        value, success = resolver(initial_value)

        if not success and initial_value is not None:
            cli.negative_feedback(neg_feedback)

        while not success:
            value = cli.ask_input(question)
            value, success = resolver(value)
            if not success:
                cli.negative_feedback(neg_feedback)
                for hint in hints:
                    cli.give_hint(hint)
            else:
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


def validate_demo_flags(demo: Optional[bool], interactive: bool) -> bool:
    """
    Checks which combination of values are contained in the parameters and returns the correct value
    for parameters.demo, eventually asking the user if necessary
    :param demo: whether the --no-demo or --with-demo flag was passed
    :param interactive: whether the script overall is allowed to ask anything to the user interactively
    :return: True if demo should be included, False otherwise
    """
    if demo is None:
        # Neither --with-demo nor --no-demo were passed
        if not interactive:
            # --not-interactive was specified - default to True
            return True
        else:
            # --not-interactive was not specified - ask
            value = cli.ask_input(
                "Do you want to install a \033[0;33mdemo application\033[0;m within your project? "
                "It's especially recommended to beginners (yes/no)")
            while True:
                if value == "n" or value == "no":
                    return False
                elif value == "y" or value == "yes":
                    return True
                else:
                    value = cli.handle_failure("Please type yes or no:")
    elif demo:
        # --with-demo was passed
        return True
    elif not demo:
        # --no-demo was passed
        return False


def validate_gitlab(repo_type, upload_protocol, clone_protocol, project_name, cern_id) -> Optional[str]:
    """
    Ensures all the parameters related to GitLab are in order.
    :return: a dictionary containing the 'gitlab' and 'repo_url' values
    """
    # Make sure the upload protocol is specified
    if upload_protocol is None:
        upload_protocol = clone_protocol

    if repo_type == 'operational':
        group = GROUP_NAME
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

    return repo_url


def validate_cern_id(cern_id: Optional[str]) -> Tuple[Optional[PhoneBookEntry], bool]:
    """
    Uses the Phonebook utilities to validate CERN IDs and retrieve their data.
    :param cern_id: The CERN ID of the user
    :return: A PhonebookEntry object containing all the user's info
    """
    if cern_id is None:
        return None, False

    phonebook = PhoneBook()
    if not phonebook.validate_login_name(cern_id):
        return None, False

    entries = phonebook.search_by_login_name(cern_id)
    if len(entries) == 1 and cern_id in entries[0].login_name:
        entry = entries[0]
        entry.login_name = entry.login_name[0]  # Assume this use has only the login name we validated it on
        return entry, True
    return None, False
