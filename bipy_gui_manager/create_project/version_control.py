from typing import Mapping, Optional
import os
import json
import urllib
try:
    import requests  # requests might not be installed, but is needed only for the avatar upload
except ImportError:
    pass
from subprocess import Popen, PIPE
from bipy_gui_manager import cli_utils as cli


def invoke_git(parameters=(), cwd=os.getcwd(), neg_feedback="An error occurred in Git!"):
    """
    Perform a syscall to the local Git executable
    :param parameters: parameters to pass to Git, as an array
    :param cwd: working directory for Git
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
            raise OSError(neg_feedback)


def authenticate_on_gitlab(username: str, password: str) -> Optional[str]:
    """
    Try to authenticate the user on GitLab
    :param username: the user's CERN username
    :param password: the user's CERN password
    :return: the token if authentication is successful, None otherwise
    """
    try:
        auth_token = post_to_gitlab(endpoint='/oauth/token',
                                    post_fields={'grant_type': 'password', 'username': username, 'password': password})
    except urllib.error.HTTPError as he:
        if he.code == 401:  # Unauthorized
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
    url = 'https://gitlab.cern.ch/{}'.format(endpoint)
    request_data = urllib.parse.urlencode(post_fields).encode()
    request = urllib.request.Request(url, data=request_data)
    response = urllib.request.urlopen(request).read().decode()
    return json.loads(response)


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


def create_gitlab_repository(project_name: str, project_desc: str, auth_token: str):
    """
    Create a GitLab repo under bisw-python
    :param project_name: Name of the project
    :param project_desc: One-line description of the project
    :param auth_token: a GitLab access token. Can be either obtained by authenticating or can be given via CLI.
    """
    repo_data = post_to_gitlab(endpoint='api/v4/projects?{}'.format(auth_token),
                               post_fields={'path': project_name,
                                            'name': project_name.replace("-", " ").title(),
                                            'description': project_desc
                                            })

    # The avatar setting honestly is not critical: if it fails, amen
    # Note: This might fail due to the lack of the 'requests' package. It's ok.
    try:
        project_id = repo_data['id']
        avatar_path = os.path.join(os.path.dirname(__file__), "resources", "PyQt-logo-gray.png")
        url = 'https://gitlab.cern.ch/api/v4/projects/{}?{}'.format(project_id, auth_token)
        avatar = {'avatar': (avatar_path, open(avatar_path, 'rb'), 'multipart/form-data')}
        requests.put(url, files=avatar)
    except Exception as e:
        print("  - Avatar upload failed: {}.".format(e))


def push_first_commit(project_path: str, gitlab_repo: str) -> None:
    """
    Adds a remote to the Git repo and pushes the first commit
    :param project_path: Path to the project root
    :param gitlab_repo: GitLab repo to push to
    """
    invoke_git(
        parameters=['remote', 'add', 'origin', gitlab_repo],
        cwd=project_path,
        neg_feedback="Failed to add the remote on the project's local repo."
    )
    # Check for repository existence
    invoke_git(
        parameters=['ls-remote'],
        cwd=project_path,
        neg_feedback="Seems like {} is not an existing and empty GitLab repository. ".format(gitlab_repo) +
                     "The repository should EXIST and be EMPTY at this stage. \n" +
                     "You can create the repo yourself and then pass the link with the --repo flag." +
                     "If you think this is a bug, please report it to the maintainers."
    )
    invoke_git(
        parameters=['push', '-u', 'origin', 'master'],
        cwd=project_path,
        neg_feedback="Failed to push the first commit to GitLab."
    )
