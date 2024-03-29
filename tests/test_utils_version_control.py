import os
import io
import shutil
import pytest
from time import sleep
from urllib.error import HTTPError
import subprocess

from bipy_gui_manager.utils import version_control
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


def test_is_git_folder(tmpdir):
    assert not version_control.is_git_folder(tmpdir)
    version_control.invoke_git(['init'], cwd=tmpdir)
    assert version_control.is_git_folder(tmpdir)


def test_init_local_repo(tmpdir):
    # A file must exist in the folder or Git will refuse to commit
    with open(tmpdir / "testfile", 'w') as f:
        f.write("test")
    version_control.init_local_repo(tmpdir)
    assert os.path.exists(tmpdir / ".git")


def test_get_git_branch(tmpdir):
    with pytest.raises(OSError):
        version_control.get_git_branch(tmpdir)
    version_control.invoke_git(['init'], cwd=tmpdir)
    assert version_control.get_git_branch(tmpdir) == "master"
    version_control.invoke_git(['checkout', '-b', 'test-branch'], cwd=tmpdir)
    assert version_control.get_git_branch(tmpdir) == "test-branch"


def test_is_git_dir_clean(tmpdir, monkeypatch):
    version_control.invoke_git(['init'], cwd=tmpdir)
    assert version_control.is_git_dir_clean(tmpdir)

    with open(tmpdir / "testfile", 'w') as f:
        f.write("test")
    assert not version_control.is_git_dir_clean(tmpdir)

    version_control.invoke_git(["add", '--all'], cwd=tmpdir)
    assert not version_control.is_git_dir_clean(tmpdir)

    version_control.invoke_git(['commit', '-m', "test"], cwd=tmpdir)
    assert version_control.is_git_dir_clean(tmpdir)

    with open(tmpdir / "testfile2", 'w') as f:
        f.write("test")
    assert not version_control.is_git_dir_clean(tmpdir)

    # TODO check the same for a repo with a remote
    version_control.invoke_git(["remote", "add", "origin",
                                "ssh://git@gitlab.cern.ch:7999/bisw-python/bipy-gui-manager.git"],
                               cwd=tmpdir)
    assert not version_control.is_git_dir_clean(tmpdir)


def test_get_remote_url(tmpdir, monkeypatch):
    assert version_control.get_remote_url(tmpdir) is None

    version_control.invoke_git(['init'], cwd=tmpdir)
    assert version_control.get_remote_url(tmpdir) is None

    version_control.invoke_git(["remote", "add", "origin",
                                "https://:@gitlab.cern.ch:8443/bisw-python/be-bi-pyqt-template.git"],
                               cwd=tmpdir)
    # The actual URL will contain the GitLab token on the CI, so comparison is not possible
    assert version_control.get_remote_url(tmpdir) is not None


def test_post_to_gitlab(tmpdir, monkeypatch):
    monkeypatch.setattr('urllib.parse.urlencode', lambda *args, **kwargs: "")
    monkeypatch.setattr('urllib.request.Request', lambda *args, **kwargs: None)
    monkeypatch.setattr('urllib.request.urlopen', lambda *args, **kwargs: io.BytesIO(b'{"test_key" : "test-value" }'))
    data = version_control.post_to_gitlab("nonexisting-test-endpoint/", {"test-post-field": "test-post-data"})
    assert data["test_key"] == "test-value"


def test_authenticate_on_gitlab_valid_credentials(tmpdir, monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.utils.version_control.post_to_gitlab',
                        lambda *a, **k: dict({'access_token': 'test-token'}))
    token = version_control.authenticate_on_gitlab("valid_username", "valid_password")
    assert token == "access_token=test-token"


def test_authenticate_on_gitlab_invalid_credentials(tmpdir, monkeypatch):
    def raise_urllib_http_error(*args, **kwargs):
        raise HTTPError(url="test-url/", code=401, msg="Test error", hdrs="", fp=None)

    monkeypatch.setattr('bipy_gui_manager.utils.version_control.post_to_gitlab', raise_urllib_http_error)
    data = version_control.authenticate_on_gitlab("valid_username", "valid_password")
    assert data is None
    

def test_git_init_and_push(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_template_files(project_path, "test-project")
    version_control.init_local_repo(project_path)
    version_control.push_first_commit(project_path, "https://gitlab.cern.ch/test-project.git")


def test_create_gitlab_repo(monkeypatch, mock_gitlab):
    try:
        monkeypatch.setattr('requests.put', lambda *args, **kwargs: '')
    except ModuleNotFoundError:
        # requests is not installed in the test environment
        pass
    monkeypatch.setattr('bipy_gui_manager.utils.version_control.authenticate_on_gitlab', lambda *a, **k: 1/0)
    version_control.create_gitlab_repository(repo_type="test",
                                             project_name="test-project",
                                             project_desc="A test project",
                                             auth_token="access_token=auth-token",
                                             author_name="me")


