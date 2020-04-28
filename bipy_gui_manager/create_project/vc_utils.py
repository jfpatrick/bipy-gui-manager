from typing import Mapping, Optional
import os
import json
import urllib
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
        cli.negative_feedback(he)
        # Probably 401 Unauthorized
        return None
    return auth_token["access_token"]


def post_to_gitlab(endpoint: str, post_fields: Mapping[str, str]) -> Mapping[str, str]:
    """
    Performs a call to a GitLab API's endpoint.
    NOTE: only JSON will be send - no binaries
    :param endpoint: the endpoint's path
    :param post_fields: what the POST request body will contain
    :return:
    """
    url = 'https://gitlab.cern.ch/{}'.format(endpoint)
    request_data = urllib.parse.urlencode(post_fields).encode()
    request = urllib.request.Request(url, data=request_data)
    response = urllib.request.urlopen(request).read().decode()
    return json.loads(response)
