from typing import Mapping, Optional, Union
import re
import os
import argparse
import getpass
from bipy_gui_manager import cli_utils as cli
from bipy_gui_manager.create_project import validation
from bipy_gui_manager.create_project import version_control
from bipy_gui_manager.create_project import phonebook


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

    username = validation.validate_as_arg_or_ask(
        cli_value=username,
        validator=lambda u: phonebook.validate_cern_id(u),
        question="Please type your \033[0;33mCERN username\033[0;m:",
        neg_feedback="This username does not exist.",
        pos_feedback="Your CERN username is set to \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )
    project_parameters["author_cern_id"] = username

    # Author full name
    project_parameters["author_full_name"] = phonebook.discover_full_name(project_parameters["author_cern_id"])
    cli.positive_feedback("Your name is set to \033[0;32m{}\033[0;m".format(project_parameters["author_full_name"]))

    # Author CERN email
    project_parameters["author_email"] = phonebook.discover_email(project_parameters["author_cern_id"])
    cli.positive_feedback("Your email is set to \033[0;32m{}\033[0;m".format(project_parameters["author_email"]))

    # Project name
    project_name_validator = re.compile("^[a-z0-9-]+$")
    project_parameters["project_name"] = validation.validate_as_arg_or_ask(
        cli_value=parameters.project_name,
        validator=lambda v: project_name_validator.match(v),
        question="Please enter your \033[0;33mproject's name\033[0;m:",
        neg_feedback="The project name can contain only lowercase letters, numbers and dashes.",
        pos_feedback="The project name is set to: \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )

    # Project description
    project_parameters["project_desc"] = validation.validate_as_arg_or_ask(
        cli_value=parameters.project_desc,
        validator=lambda v: v != "" and "\"" not in v,
        question="Please enter a \033[0;33mone-line description\033[0;m of your project:",
        neg_feedback="The project description cannot contain the character \".",
        pos_feedback="The project description is set to: \033[0;32m{}\033[0;m",
        interactive=parameters.interactive
    )

    # Path to project
    project_parameters["base_path"] = validation.validate_as_arg_or_ask(
        cli_value=parameters.base_path,
        validator=lambda v: validation.validate_base_path(v,
                                                          project_parameters["project_name"],
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

    # GitLab URL - adds the keys gitlab, repo_url, create_repo
    project_parameters.update(validation.validate_gitlab(parameters.gitlab,
                                                         parameters.gitlab_repo,
                                                         parameters.interactive,
                                                         parameters.upload_protocol,
                                                         parameters.clone_protocol,
                                                         project_parameters["project_name"]))

    # GitLab authorization token
    if project_parameters["gitlab"] and project_parameters["create_repo"]:
        if parameters.gitlab_token is None:
            project_parameters["author_token"] = authenticate_user(project_parameters["author_cern_id"])
        else:
            # TODO Validate token early!
            project_parameters["author_token"] = "private_token={}".format(parameters.gitlab_token)

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



