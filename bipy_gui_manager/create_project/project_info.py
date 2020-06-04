from typing import Mapping, Optional, Union
import re
import os
import logging
import getpass
import argparse
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
        logging.debug("Username found among the CLI arguments: {}".format(username))
    else:
        username = getpass.getuser()
        logging.debug("Username obtained from getpass: {}".format(username))
    cli.positive_feedback("Looking for \033[0;32m{}\033[0;m info on Phonebook".format(username))

    logging.debug("Validating username in PhoneBook if previously found...".format(username))
    phonebook_entry = validation.resolve_as_arg_or_ask(
        initial_value=username,
        resolver=lambda u: validation.validate_cern_id(u),
        question="Please type your \033[0;33mCERN username\033[0;m:",
        neg_feedback="This username does not exist.",
        interactive=parameters.interactive
    )
    project_parameters["author_cern_id"] = phonebook_entry.login_name
    cli.positive_feedback("Your CERN username is set to \033[0;32m{}\033[0;m ".format(
        project_parameters["author_cern_id"]), newline=False)

    # Author full name
    logging.debug("Obtaining full name for {} from PhoneBook".format(username))
    project_parameters["author_full_name"] = phonebook_entry.full_name[0]
    cli.positive_feedback("Your name is set to \033[0;32m{}\033[0;m".format(project_parameters["author_full_name"]),
                          newline=False)

    # Author CERN email
    logging.debug("Obtaining email for {} from PhoneBook".format(username))
    project_parameters["author_email"] = phonebook_entry.email[0]
    cli.positive_feedback("Your email is set to \033[0;32m{}\033[0;m".format(project_parameters["author_email"]))

    # Project name
    logging.debug("Collecting project name")
    project_name_validator = re.compile("^[a-z0-9-]+$")
    project_parameters["project_name"] = validation.resolve_as_arg_or_ask(
        initial_value=parameters.project_name,
        resolver=lambda v: (v, v is not None and project_name_validator.match(str(v))),
        question="Please enter your \033[0;33mproject's name\033[0;m:",
        neg_feedback="The project name can contain only lowercase letters, digits, dashes and cannot be left empty.",
        interactive=parameters.interactive
    )
    cli.positive_feedback("The project name is set to: \033[0;32m{}\033[0;m".format(project_parameters["project_name"]))

    # Project description
    logging.debug("Collecting project description")
    project_parameters["project_desc"] = validation.resolve_as_arg_or_ask(
        initial_value=parameters.project_desc,
        resolver=lambda v: (v, v is not None and v != "" and "\"" not in str(v)),
        question="Please enter a \033[0;33mone-line description\033[0;m of your project:",
        neg_feedback="The project description cannot be None and cannot contain the character \".",
        interactive=parameters.interactive
    )
    cli.positive_feedback("The project description is set to: \033[0;32m{}\033[0;m".format(
        project_parameters["project_desc"]))

    # Path to project
    logging.debug("Collecting project base path")
    project_parameters["base_path"] = validation.resolve_as_arg_or_ask(
        initial_value=parameters.base_path,
        resolver=lambda v: validation.validate_base_path(v, project_parameters["project_name"],
                                                         parameters.interactive,
                                                         parameters.overwrite),
        question="Please type the \033[0;33mpath\033[0;m where to create the new project, or type '.' to create it "
                 "in the current directory ({}):".format(os.getcwd()),
        neg_feedback="Please provide a valid path.",
        interactive=parameters.interactive
    )
    project_parameters["project_path"] = os.path.join(project_parameters["base_path"],
                                                      project_parameters["project_name"])
    cli.positive_feedback("The project will be created under \033[0;32m{}\033[0;m".format(
        project_parameters["project_path"]))

    # Demo is required
    logging.debug("Collecting demo request")
    project_parameters["demo"] = validation.validate_demo_flags(parameters.demo, parameters.interactive)
    if project_parameters["demo"]:
        cli.positive_feedback("Your project will contain a demo application.")
    else:
        cli.positive_feedback("Your project will not contain the demo application.")

    # GitLab URL
    if parameters.gitlab:
        logging.debug("Collecting GitLab configuration")
        project_parameters["repo_type"] = validation.resolve_as_arg_or_ask(
            initial_value=parameters.gitlab_repo,
            resolver=lambda v: (v, v == "operational" or v == "test"),
            question="Operational GUI will be hosted under https://gitlab.cern.ch/bisw-python, while personal tests "
                     "go into your personal GitLab space. Note that tests can be upgraded to operational, while the "
                     "contrary requires manual intervention. Is this project \033[0;33moperational\033[0;m or a "
                     "personal \033[0;33mtest\033[0;m? (operational/test)",
            neg_feedback="Please type 'operational' or 'test'",
            interactive=parameters.interactive
        )
        logging.debug("Validate configuration passed")
        project_parameters["repo_url"] = validation.validate_gitlab(repo_type=project_parameters["repo_type"],
                                                                    upload_protocol=parameters.upload_protocol,
                                                                    clone_protocol=parameters.clone_protocol,
                                                                    project_name=project_parameters["project_name"],
                                                                    cern_id=project_parameters["author_cern_id"])
        cli.positive_feedback("Your project type is set to \033[0;32m{}\033[0;m".format(
            project_parameters["repo_type"]), newline=False)
        cli.positive_feedback("Your project's GitLab repository will be created under \033[0;32m{}\033[0;m".format(
            project_parameters["repo_url"]))

        if project_parameters["repo_type"] == "test":
            project_parameters["gitlab_space"] = phonebook_entry.login_name
        else:
            project_parameters["gitlab_space"] = "bisw-python"

        # GitLab authorization token
        if parameters.gitlab_token is None:
            logging.debug("Collecting GitLab credentials")
            project_parameters["author_token"] = authenticate_user(project_parameters["author_cern_id"])
        else:
            # TODO Validate token!
            logging.debug("A GitLab token was passed")
            project_parameters["author_token"] = "private_token={}".format(parameters.gitlab_token)
        cli.positive_feedback("You have been successfully authenticated on GitLab.")

    else:
        logging.debug("--no-gitlab was passed, no need to collect GitLab configuration")

    # Template path (light validation)
    if parameters.template_path:
        logging.debug("A template path was passed: {}".format(parameters.template_path))
        if os.path.isdir(parameters.template_path):
            project_parameters["template_path"] = parameters.template_path
        else:
            raise ValueError("The template_path value ({}) is not a directory.".format(parameters.template_path))

    if parameters.template_url:
        # No real validation possible
        logging.debug("A template URL was passed: {}".format(parameters.template_url))
        project_parameters["template_url"] = parameters.template_url

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



