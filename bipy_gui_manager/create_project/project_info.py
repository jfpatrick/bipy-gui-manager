from typing import Mapping, Optional, Union
import re
import os
import argparse
import getpass
from bipy_gui_manager import cli_utils as cli
from bipy_gui_manager.create_project import validation
from bipy_gui_manager.create_project import version_control


def collect(parameters: argparse.Namespace) -> Mapping[str, Union[str, bool]]:
    """
    Collects the information from the user. Might be interactive or not,
    depending on the user settings and the validation outcome.
    :param parameters: CLI parameters
    :return: the validated and updated CLI arguments
    """
    project_parameters = {}

    # CERN Username
    if parameters.project_author:
        username = parameters.project_author
    else:
        username = getpass.getuser()
    cli.positive_feedback("Looking for \033[0;32m{}\033[0;m info on Phonebook".format(username))

    phonebook_entry = validation.resolve_as_arg_or_ask(
        initial_value=username,
        resolver=lambda u: validation.validate_cern_id(u),
        question="Please type your \033[0;33mCERN username\033[0;m:",
        neg_feedback="This username does not exist.",
        interactive=parameters.interactive
    )
    project_parameters["author_cern_id"] = username
    cli.positive_feedback("Your CERN username is set to \033[0;32m{}\033[0;m ".format(username), newline=False)

    # Author full name
    project_parameters["author_full_name"] = phonebook_entry.display_name
    cli.positive_feedback("Your name is set to \033[0;32m{}\033[0;m".format(project_parameters["author_full_name"]),
                          newline=False)

    # Author CERN email
    project_parameters["author_email"] = phonebook_entry.emails[0]
    cli.positive_feedback("Your email is set to \033[0;32m{}\033[0;m".format(project_parameters["author_email"]))

    # Project name
    project_name_validator = re.compile("^[a-z0-9-]+$")
    project_parameters["project_name"] = validation.resolve_as_arg_or_ask(
        initial_value=parameters.project_name,
        resolver=lambda v: (v, project_name_validator.match(str(v))),
        question="Please enter your \033[0;33mproject's name\033[0;m:",
        neg_feedback="The project name can contain only lowercase letters, numbers and dashes.",
        pos_feedback="The project name is set to: \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )

    # Project description
    project_parameters["project_desc"] = validation.resolve_as_arg_or_ask(
        initial_value=parameters.project_desc,
        resolver=lambda v: (v, v != "" and "\"" not in v),
        question="Please enter a \033[0;33mone-line description\033[0;m of your project:",
        neg_feedback="The project description cannot contain the character \".",
        pos_feedback="The project description is set to: \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )

    # Path to project
    project_parameters["base_path"] = validation.resolve_as_arg_or_ask(
        initial_value=parameters.base_path,
        resolver=lambda v: validation.validate_base_path(v, project_parameters["project_name"],
                                                         parameters.interactive,
                                                         parameters.overwrite),
        question="Please type the \033[0;33mpath\033[0;m where to create the new project, or type '.' to create it "
                 "in the current directory ({}):".format(os.getcwd()),
        neg_feedback="Please provide a valid path.",
        pos_feedback="The project will be created under \033[0;32m{}\033[0;m".format(
            os.path.join("{}", project_parameters["project_name"])),
        interactive=parameters.interactive
    )
    project_parameters["project_path"] = os.path.join(project_parameters["base_path"],
                                                      project_parameters["project_name"])

    # Demo is required
    project_parameters["demo"] = validation.validate_demo_flags(parameters.force_demo, parameters.demo,
                                                                parameters.interactive)

    # GitLab URL
    if parameters.gitlab:
        project_parameters["repo_type"] = validation.resolve_as_arg_or_ask(
            initial_value=parameters.gitlab_repo,
            resolver=lambda v: (v, v == "operational" or v == "test"),
            question="Operational GUI will be hosted under https://gitlab.cern.ch/bisw-python, while personal tests "
                     "go into your personal GitLab space. Note that tests can be upgraded to operational, while the "
                     "contrary requires manual intervention. Is this project \033[0;33moperational\033[0;m or a "
                     "personal \033[0;33mtest\033[0;m? (operational/test)",
            neg_feedback="Please type 'operational' or 'test'",
            pos_feedback="Your project type is set to \033[0;32m{}\033[0;m",
            interactive=parameters.interactive
        )
        project_parameters["repo_url"] = validation.validate_gitlab(gitlab=parameters.gitlab,
                                                                    repo_type=project_parameters["repo_type"],
                                                                    upload_protocol=parameters.upload_protocol,
                                                                    clone_protocol=parameters.clone_protocol,
                                                                    project_name=project_parameters["project_name"],
                                                                    cern_id=project_parameters["author_cern_id"])

    # GitLab authorization token
    if parameters.gitlab:
        if parameters.gitlab_token is None:
            project_parameters["author_token"] = authenticate_user(project_parameters["author_cern_id"])
        else:
            # TODO Validate token!
            project_parameters["author_token"] = "private_token={}".format(parameters.gitlab_token)
        cli.positive_feedback("You have been successfully authenticated on GitLab.")

    # Template path (light validation)
    if parameters.template_path:
        if os.path.isdir(parameters.template_path):
            project_parameters["template_path"] = parameters.template_path
        else:
            raise ValueError("The template_path value ({}) is not a directory.".format(parameters.template_path))

    return project_parameters


def authenticate_user(username: str) -> Optional[str]:
    """
    Tries to interactively authenticate a user on GitLab.
    :param username: user to authenticate
    :return: the authentication token obtained.
    """
    while True:
        pwd_prompt = "\033[0;33m=>\033[0;m Please enter your CERN password (to authenticate you on GitLab):  "
        token = version_control.authenticate_on_gitlab(username, getpass.getpass(pwd_prompt))
        if token is None:
            cli.negative_feedback("Authentication failed.")
        else:
            return token



