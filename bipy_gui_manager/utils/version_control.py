from typing import Mapping, Optional, Tuple, Union
import os
import json
import urllib
import logging
from pathlib import Path
from urllib.error import HTTPError
try:
    import requests  # requests might not be installed, but is needed only for the avatar upload
except ImportError:
    pass
from subprocess import Popen, PIPE
from bipy_gui_manager.create_project.constants import GROUP_ID


def invoke_git(parameters=(), cwd=os.getcwd(), neg_feedback="An error occurred in Git!") -> Tuple[str, str]:
    """
    Perform a syscall to the local Git executable
    :param parameters: parameters to pass to Git, as an array
    :param cwd: working directory for Git
    :param neg_feedback: message to explain a potential failure
    :return (stdout, stderr) if successful
    :raises OSError if it fails
    """
    logging.debug("invoke_git received the following parameters: {}".format(parameters))
    command = ['/usr/bin/git']
    command.extend(parameters)

    while True:
        git_query = Popen(command, cwd=cwd, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = git_query.communicate()

        if git_query.poll() == 0:
            logging.debug("invoke_git was successful")
            logging.debug(f"Err: {stderr.decode('utf-8')}")
            logging.debug(f"Out: {stdout.decode('utf-8')}")
            return stdout.decode('utf-8'), stderr.decode('utf-8')
        else:
            logging.debug(stdout.decode('utf-8') + "  -  " + stderr.decode('utf-8'))
            raise OSError(neg_feedback)


def is_git_folder(path_to_check: Union[str, Path]):
    """
    Checks if the given folder is a Git repo.
    :param path_to_check: this path should be a Git repository
    :return: True if 'git status' returns exit code 0, False otherwise
    """
    try:
        invoke_git(parameters=['status'], cwd=path_to_check)
        return True
    except OSError:
        return False


def init_local_repo(project_path: str) -> None:
    """
    Initialize the project's git repo.
    :param project_path: Path to the project root
    :return nothing, but inits the local Git repository
    """
    invoke_git(
        parameters=['init'],
        cwd=project_path,
        neg_feedback="Failed to init the repo in the project folder."
    )
    invoke_git(
        parameters=['add', '--all'],
        cwd=project_path,
        neg_feedback="Failed to stage the template."
    )
    invoke_git(
        parameters=['commit', '-m', 'Initial commit ' +
                    '(from bipy-gui-manager https://gitlab.cern.ch/bisw-python/bipy_gui_manager)'],
        cwd=project_path,
        neg_feedback="Failed to commit the template."
    )


def get_git_branch(path_to_check: Union[str, Path]):
    """
    Returns the branch the repo is currently on.
    :param path_to_check: this path should be a Git repository
    :return: the name of the current branch (i.e. master)
    :raises OsError if it's not a Git repo or any other issue is encountered.
    """
    stdout, stderr = invoke_git(parameters=['status'], cwd=path_to_check)
    if stderr:
        raise OSError(f"Git raised an exception:\n{stderr}")

    if not stdout.splitlines()[0].startswith("# On branch "):
        raise OSError(f"Git returned an unexpected message:\n{stdout}")

    return stdout.splitlines()[0].lstrip("# On branch ").strip()


def is_git_dir_clean(path_to_check: Union[str, Path]):
    """
    Checks if the repo is clean (i.e. no commits to push and no uncommitted changes.)
    :param path_to_check: this path should be a Git repository
    :return: True if there are no commits to push and no uncommitted changes, False otherwise
    :raises OsError if it's not a Git repo or any other issue parsing Git's reply is encountered.
    """
    stdout, stderr = invoke_git(parameters=['status'], cwd=path_to_check)
    logging.debug(stdout + "  -  " + stderr)

    if stderr:
        raise OSError(f"Git raised an exception:\n{stderr}")

    for line in stdout.splitlines():

        # Unstaged, uncommitted modifications
        if line.startswith("# Untracked files:"):
            return False

        # Staged, uncommitted modifications
        if line.startswith("# Changes to be committed:"):
            return False

        # Untracked files
        if line.startswith("# Untracked files:"):
            return False

        # Commits not pushed
        if line.startswith("# Your branch is ahead of"):
            return False

    if "nothing to commit" in stdout.splitlines()[-1]:
        return True

    return False


def get_remote_url(path_to_repo: Union[str, Path]) -> Optional[str]:
    """
    Returns the remote URL of master for the given repo.
    Assumes the remote is called 'origin' and returns the Fetch URL.
    Returns None if the repo has no remote for origin.
    Raises OsError if the path does not correspond to a Git repo.
    :param path_to_repo: the repo to find the remote of
    :return: the remote for origin if exists, None otherwise
    """
    try:
        stdout, stderr = invoke_git(parameters=['remote', 'show', 'origin'], cwd=path_to_repo)
        logging.debug(stdout + "  -  " + stderr)
        for line in stdout.splitlines():
            if line.strip().startswith("Fetch URL:"):
                return line.strip()[len("Fetch URL:"):].strip()
        return None

    except OSError as e:
        logging.debug("Git raised 'origin does not appear to be a git repository' error.")
        if "'origin' does not appear to be a git repository" in str(e):
            return None


def authenticate_on_gitlab(username: str, password: str) -> Optional[str]:
    """
    Try to authenticate the user on GitLab
    :param username: the user's CERN username
    :param password: the user's CERN password
    :return: the token if authentication is successful, None otherwise
    """
    try:
        logging.debug("Authenticating user {} on GitLab".format(username))
        auth_token = post_to_gitlab(endpoint='/oauth/token',
                                    post_fields={'grant_type': 'password', 'username': username, 'password': password})
    except HTTPError as he:
        if he.code == 401:  # Unauthorized
            logging.debug("Authentication on GitLab failed (the server returned a code 401)")
            return None
        else:
            raise he
    return "access_token={}".format(auth_token["access_token"])


def post_to_gitlab(endpoint: str, post_fields: Mapping[str, str]) -> Mapping[str, str]:
    """
    Performs a call to a GitLab API's endpoint.
    NOTE: only JSON will be send - no binaries
    :param endpoint: the endpoint's path
    :param post_fields: what the POST request body will contain
    :return: the eventual response, decoded from JSON
    """
    logging.debug("POSTing to GitLab's endpoint https://gitlab.cern.ch/{} the following fields: {}".format(endpoint,
                                                                                                   post_fields.keys()))
    url = 'https://gitlab.cern.ch/{}'.format(endpoint)
    request_data = urllib.parse.urlencode(post_fields).encode()
    request = urllib.request.Request(url, data=request_data)
    response = urllib.request.urlopen(request).read().decode()
    logging.info("Server responds: {}".format(response))
    return json.loads(response)


def create_gitlab_repository(repo_type: str, project_name: str, project_desc: str, auth_token: str):
    """
    Create a GitLab repo under bisw-python
    :param project_name: Name of the project
    :param project_desc: One-line description of the project
    :param auth_token: a GitLab access token. Can be either obtained by authenticating or can be given via CLI.
    """
    post_fields = {'path': project_name,
                   'name': project_name.replace("-", " ").title(),
                   'description': project_desc}

    if repo_type == "operational":
        post_fields['namespace_id'] = str(GROUP_ID)

    repo_data = post_to_gitlab(endpoint='api/v4/projects?{}'.format(auth_token),
                               post_fields=post_fields)

    project_id = repo_data['id']

    # Add the acc-py docserver GitLab user, so it can build documentation for private repos
    post_to_gitlab(endpoint='api/v4/projects/{}/members?{}'.format(project_id, auth_token),
                   post_fields={
                       'user_id': '19185',  # accpydocserver's user ID
                       'access_level': '20',
                   })

    # The avatar setting honestly is not critical: if it fails, amen
    # Note: This might fail due to the lack of the 'requests' package. It's ok.
    try:
        avatar_path = os.path.join(os.path.dirname(__file__), "resources", "PyQt-logo-gray.png")
        url = 'https://gitlab.cern.ch/api/v4/projects/{}?{}'.format(project_id, auth_token)
        avatar = {'avatar': (avatar_path, open(avatar_path, 'rb'), 'multipart/form-data')}
        requests.put(url, files=avatar)
    except Exception as e:
        print("  - Avatar upload failed: {}.".format(e))


def push_first_commit(project_path: str, repo_url: str) -> None:
    """
    Adds a remote to the Git repo and pushes the first commit
    :param project_path: Path to the project root
    :param repo_url: GitLab repo to push to
    """
    invoke_git(
        parameters=['remote', 'add', 'origin', repo_url],
        cwd=project_path,
        neg_feedback="Failed to add the remote on the project's local repo."
    )
    # Check for repository existence
    invoke_git(
        parameters=['ls-remote'],
        cwd=project_path,
        neg_feedback="Seems like {} is not an existing and empty GitLab repository. ".format(repo_url) +
                     "The repository should EXIST and be EMPTY at this stage. \n" +
                     "You can create the repo yourself and then pass the link with the --repo flag." +
                     "If you think this is a bug, please report it to the maintainers."
    )
    invoke_git(
        parameters=['push', '-u', 'origin', 'master'],
        cwd=project_path,
        neg_feedback="Failed to push the first commit to GitLab."
    )
