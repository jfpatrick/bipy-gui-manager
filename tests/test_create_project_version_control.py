import os
import io
import pytest
import urllib
import subprocess
from bipy_gui_manager.create_project import version_control
from .conftest import create_template_files


class MockSuccessfulPopen:

    def __init__(self, command, cwd, stdout, stderr):
        pass

    def communicate(self):
        return "test stdout".encode('utf-8'), "".encode('utf-8')

    def poll(self):
        return 0


class MockFailingPopen:

    def __init__(self, command, cwd, stdout, stderr):
        pass

    def communicate(self):
        return "test stdout".encode('utf-8'), "test stderr".encode('utf-8')

    def poll(self):
        return 1


def test_invoke_git(tmpdir, monkeypatch):
    version_control.Popen = MockSuccessfulPopen
    version_control.invoke_git(['not_a_git_command'], cwd=tmpdir, neg_feedback="Test Feedback")
    version_control.Popen = MockFailingPopen
    with pytest.raises(OSError):
        version_control.invoke_git(['not_a_git_command'], cwd=tmpdir, neg_feedback="Test Feedback")
    version_control.Popen = subprocess.Popen


def test_post_to_gitlab(tmpdir, monkeypatch):
    monkeypatch.setattr('urllib.parse.urlencode', lambda *args, **kwargs: "")
    monkeypatch.setattr('urllib.request.Request', lambda *args, **kwargs: None)
    monkeypatch.setattr('urllib.request.urlopen', lambda *args, **kwargs: io.BytesIO(b'{"test_key" : "test-value" }'))
    data = version_control.post_to_gitlab("nonexisting-test-endpoint/", {"test-post-field": "test-post-data"})
    assert data["test_key"] == "test-value"


def test_authenticate_on_gitlab_valid_credentials(tmpdir, monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.version_control.post_to_gitlab',
                        lambda *a, **k: dict({'access_token': 'test-token'}))
    token = version_control.authenticate_on_gitlab("valid_username", "valid_password")
    assert token == "access_token=test-token"


def test_authenticate_on_gitlab_invalid_credentials(tmpdir, monkeypatch):
    def raise_urllib_http_error(*args, **kwargs):
        raise urllib.error.HTTPError(url="test-url/", code=401, msg="Test error", hdrs="", fp=None)

    monkeypatch.setattr('bipy_gui_manager.create_project.version_control.post_to_gitlab', raise_urllib_http_error)
    data = version_control.authenticate_on_gitlab("valid_username", "valid_password")
    assert data is None
    

def test_git_init_and_push(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_template_files(project_path, "test-project", True)
    version_control.init_local_repo(project_path)
    version_control.push_first_commit(project_path, "https://gitlab.cern.ch/test-project.git")


def test_create_gitlab_repo(monkeypatch):
    try:
        monkeypatch.setattr('requests.put', lambda *args, **kwargs: '')
    except ModuleNotFoundError:
        # requests is not installed in the test environment
        pass
    monkeypatch.setattr('bipy_gui_manager.create_project.version_control.post_to_gitlab', lambda *args, **kwargs: "")
    monkeypatch.setattr('bipy_gui_manager.create_project.version_control.authenticate_on_gitlab', lambda *args, **kwargs: 1/0)
    version_control.create_gitlab_repository("test-project", "A test project", auth_token="access_token=auth-token")


