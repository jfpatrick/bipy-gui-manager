import io
import pytest
import urllib
import subprocess
import bipy_gui_manager.create_project.vc_utils as vc_utils


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
    vc_utils.Popen = MockSuccessfulPopen
    vc_utils.invoke_git(['not_a_git_command'], cwd=tmpdir, allow_retry=False, neg_feedback="Test Feedback")
    vc_utils.Popen = MockFailingPopen
    with pytest.raises(OSError):
        vc_utils.invoke_git(['not_a_git_command'], cwd=tmpdir, allow_retry=False, neg_feedback="Test Feedback")
    vc_utils.Popen = subprocess.Popen


def test_post_to_gitlab(tmpdir, monkeypatch):
    monkeypatch.setattr('urllib.parse.urlencode', lambda *args, **kwargs: "")
    monkeypatch.setattr('urllib.request.Request', lambda *args, **kwargs: None)
    monkeypatch.setattr('urllib.request.urlopen', lambda *args, **kwargs: io.BytesIO(b'{"test_key" : "test-value" }'))
    data = vc_utils.post_to_gitlab("nonexisting-test-endpoint/", {"test-post-field": "test-post-data"})
    assert data["test_key"] == "test-value"


def test_authenticate_on_gitlab_valid_credentials(tmpdir, monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.vc_utils.post_to_gitlab',
                        lambda *a, **k: dict({'access_token': 'test-token'}))
    token = vc_utils.authenticate_on_gitlab("valid_username", "valid_password")
    assert token == "test-token"


def test_authenticate_on_gitlab_invalid_credentials(tmpdir, monkeypatch):
    def raise_urllib_http_error(*args, **kwargs):
        raise urllib.error.HTTPError(url="test-url/", code=401, msg="Test error", hdrs="", fp=None)

    monkeypatch.setattr('bipy_gui_manager.create_project.vc_utils.post_to_gitlab', raise_urllib_http_error)
    data = vc_utils.authenticate_on_gitlab("valid_username", "valid_password")
    assert data is None
