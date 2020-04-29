from typing import Mapping, Union
import os
import re
import shutil
from bipy_gui_manager import cli_utils as cli
from bipy_gui_manager.create_project import GROUP_NAME


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


def validate_as_arg_or_ask(cli_value, validator, question, neg_feedback, pos_feedback=None, hints=(), interactive=True):
    """
        If an initial value is given and valid, return it.
        If an initial value is given and invalid, fail.
        If it's not given, ask the user until a valid value is received.
        if interactive is False, fail rather than asking.
    """
    if not interactive and cli_value is None:
        raise ValueError(neg_feedback)
    if cli_value is not None or not interactive:
        result = validate_or_fail(cli_value, validator, neg_feedback)
        if pos_feedback:
            cli.positive_feedback(pos_feedback.format(result))
        return result
    else:
        return validate_or_ask(validator, question, neg_feedback, pos_feedback=pos_feedback, hints=hints)


def validate_base_path(base_path: str, project_name: str, interactive: bool = True, overwrite: bool = False) -> bool:
    """
    Makes sure there is no folder with the name of the new project and if so ask the user and act accordingly.
    :param base_path: path to the new project
    :param project_name: name of the folder for the new project
    :param interactive: whether the use should be asked what to do if the path exist
    :param overwrite: whether to automatically overwrite the existing folder
    :return True if the path is available
    """
    project_path = os.path.join(base_path, project_name)
    if os.path.exists(project_path):
        if overwrite:
            cli.list_subtask("Overwriting folder {}".format(project_path))
            shutil.rmtree(project_path)
            return True
        elif not interactive:
            raise OSError("Directory '{}' already exists.".format(project_path))
        else:
            answer = cli.handle_failure("A folder called '{}' already exists. ".format(project_path) +
                                        "Do you want to overwrite it or to enter another path? (overwrite/another)")
            if answer == "overwrite":
                cli.list_subtask("Overwriting existing folder")
                shutil.rmtree(project_path)
    return True


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


def validate_gitlab(gitlab, repo, interactive, upload_protocol, clone_protocol, project_name) \
        -> Mapping[str, Union[str, bool, None]]:
    """
    Ensures all the parameters related to GitLab are in order.
    :return: a dictionary containing the 'gitlab', 'create_repo' and 'repo_url' values
    """
    if gitlab:
        # Validate explicit repo values
        repo_validator_ssh = re.compile("^ssh://git@gitlab.cern.ch:7999/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")
        repo_validator_https = re.compile("^https://gitlab.cern.ch/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")
        repo_validator_kerb = re.compile("^https://:@gitlab.cern.ch:8443/[a-zA-Z0-9_%-]+/[a-zA-Z0-9_%/-]+.git$")
        repo = validate_as_arg_or_ask(
            cli_value=repo,
            validator=lambda v: (v is not None and (
                                 v == "" or
                                 v == "default" or
                                 v == "no-gitlab" or
                                 repo_validator_https.match(v) or
                                 repo_validator_ssh.match(v) or
                                 repo_validator_kerb.match(v))),
            question="Press ENTER to create a GitLab repository for your project under 'bisw-python', or enter your "
                     "existing GitLab repository address here (or type 'no-gitlab' to keep your repository local):",
            neg_feedback="Invalid GitLab repository URL.",
            pos_feedback="The project GitLab repository address is set to: \033[0;32m{}\033[0;m",
            hints=("copy the address from the Clone button, choosing the protocol you prefer (HTTPS, SSH, KRB5)", ),
            interactive=interactive
        )
        # Resolve 'no-gitlab' and ''
        if repo == 'no-gitlab':
            repo = None
            gitlab = False
        if repo == '':
            repo = "default"

        # Make sure to remember whether the repo should be created or not
        create_repo = repo == 'default'

        # Resolve 'default' by protocol
        if repo == 'default':

            # Make sure the protocol is specified
            if upload_protocol is None:
                upload_protocol = clone_protocol

            if upload_protocol == 'ssh':
                repo = "ssh://git@gitlab.cern.ch:7999/{}/{}.git".format(GROUP_NAME, project_name)
            elif upload_protocol == 'https':
                repo = "https://gitlab.cern.ch/{}/{}.git".format(GROUP_NAME, project_name)
            elif upload_protocol == 'kerberos':
                repo = "https://:@gitlab.cern.ch:8443/{}/{}.git".format(GROUP_NAME, project_name)
            else:
                raise ValueError("Upload protocol not recognized: '{}'".format(upload_protocol))

    else:
        create_repo = False
        repo = None

    return {
        "gitlab": gitlab,
        "repo_url": repo,
        "create_repo": create_repo,
    }

