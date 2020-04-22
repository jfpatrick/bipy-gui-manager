import pytest
import subprocess
import bipy_gui_manager.create_project.utils as utils


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
    utils.Popen = MockSuccessfulPopen
    utils.invoke_git(['not_a_git_command'], cwd=tmpdir, allow_retry=False, neg_feedback="Test Feedback")
    utils.Popen = MockFailingPopen
    with pytest.raises(OSError):
        utils.invoke_git(['not_a_git_command'], cwd=tmpdir, allow_retry=False, neg_feedback="Test Feedback")
    utils.Popen = subprocess.Popen


def test_validate_or_fail():
    # Value is valid
    assert "test value" == utils.validate_or_fail("test value", lambda v: "test" in v, "neg test feedback")
    # Value is not valid
    with pytest.raises(ValueError):
        utils.validate_or_fail("test value", lambda v: "test" not in v, "neg test feedback")


def test_validate_or_ask(monkeypatch):
    # Valid value
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    assert "test value" == utils.validate_or_ask(lambda v: "test" in v, "Test question", "test Neg Feedback",
                                                 start_value="test value")
    # Not valid value - ask
    monkeypatch.setattr('builtins.input', lambda _: "valid value")
    assert "valid value" == utils.validate_or_ask(lambda v: "test" not in v, "Test question", "test Neg Feedback",
                                                  start_value="test value")

    # No value - ask
    monkeypatch.setattr('builtins.input', lambda _: "test value")
    assert "test value" == utils.validate_or_ask(lambda v: "test" in v, "Test question", "test Neg Feedback")


def test_validate_as_arg_or_ask(monkeypatch):
    # If an initial value is given and valid, return it.
    assert "test value" == utils.validate_as_arg_or_ask("test value", lambda v: "test" in v, "Question",
                                                        "test Neg Feedback")
    # If an initial value is given and invalid, fail.
    with pytest.raises(ValueError):
        utils.validate_as_arg_or_ask("test value", lambda v: "test" not in v, "Question", "test Neg Feedback")

    # If it's not given, ask the user until a valid value is received.
    monkeypatch.setattr('builtins.input', lambda _: "test value")
    assert "test value" == utils.validate_as_arg_or_ask(None, lambda v: "test" in v, "Question", "test Neg Feedback")

    # if interactive is False, fail rather than asking.
    with pytest.raises(ValueError):
        utils.validate_as_arg_or_ask(None, lambda v: "test" not in v, "Question", "test Neg Feedback",
                                     interactive=False)


def test_validate_demo_flags(monkeypatch):
    # Non interactive cases
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    assert utils.validate_demo_flags(force_demo=True, demo=True, interactive=True)
    assert not utils.validate_demo_flags(force_demo=False, demo=False, interactive=True)
    assert utils.validate_demo_flags(force_demo=False, demo=True, interactive=False)
    # Interactive cases
    monkeypatch.setattr('builtins.input', lambda _: "yes")
    assert utils.validate_demo_flags(force_demo=False, demo=True, interactive=True)
    monkeypatch.setattr('builtins.input', lambda _: "no")
    assert not utils.validate_demo_flags(force_demo=False, demo=True, interactive=True)
