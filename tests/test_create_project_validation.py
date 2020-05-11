import os
import pytest
from bipy_gui_manager.create_project import validation


@pytest.fixture()
def mock_group_name(monkeypatch):
    # NOTE: this fixture lives here because it's custom to the validation module.
    monkeypatch.setattr('bipy_gui_manager.create_project.validation.GROUP_NAME', 'test-group')


# ################################
# #     Resolve as Arg or Ask    #
# ################################
def test_resolve_as_arg_or_ask_given_valid(monkeypatch):
    # If an initial value is given and valid, return it.
    assert "test value" == validation.resolve_as_arg_or_ask("test value", lambda v: (v, "test" in str(v)), "Question",
                                                            "test Neg Feedback")


def test_resolve_as_arg_or_ask_given_invalid(monkeypatch):
    # If an initial value is given and invalid, ask.
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    with pytest.raises(ZeroDivisionError):
        validation.resolve_as_arg_or_ask(initial_value="test value", resolver=lambda v: (v, "test" not in str(v)),
                                         question="Question", neg_feedback="test Neg Feedback")


def test_resolve_as_arg_or_ask_not_given(monkeypatch):
    # If it's not given, ask the user until a valid value is received.
    monkeypatch.setattr('builtins.input', lambda _: "test value")
    assert "test value" == validation.resolve_as_arg_or_ask(None,
                                                            lambda v: (v, "test" in str(v)), "Question", "test Neg Feedback")


def test_resolve_as_arg_or_ask_not_given_not_interactive(monkeypatch):
    # if interactive is False, fail rather than asking.
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ValueError):
        validation.resolve_as_arg_or_ask(initial_value=None, resolver=lambda v: (v, "test" in str(v)),
                                         question="Question", neg_feedback="test Neg Feedback",
                                         interactive=False)

# #########################
# #       Repo URL        #
# #########################
def test_repo_type_operational(monkeypatch, mock_group_name):
    args = {'clone_protocol': "ssh", 'project_name': "test-project",
            'upload_protocol': "https", 'repo_type': 'operational', 'cern_id': "me"}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "https://gitlab.cern.ch/test-group/test-project.git"


def test_repo_type_test(monkeypatch, mock_group_name):
    args = {'clone_protocol': "ssh", 'project_name': "test-project",
            'upload_protocol': "https", 'repo_type': 'test', 'cern_id': "me"}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "https://gitlab.cern.ch/me/test-project.git"


def test_repo_type_wrong(monkeypatch, mock_group_name):
    args = {'clone_protocol': "ssh", 'project_name': "test-project",
            'upload_protocol': "https", 'repo_type': 'wrong', 'cern_id': "me"}
    with pytest.raises(ValueError):
        validation.validate_gitlab(**args)


def test_repo_type_missing(monkeypatch, mock_group_name):
    args = {'clone_protocol': "ssh", 'project_name': "test-project",
            'upload_protocol': "https", 'repo_type': None, 'cern_id': "me"}
    with pytest.raises(ValueError):
        validation.validate_gitlab(**args)


# #########################
# #    Upload Protocol    #
# #########################
def test_upload_protocol_not_given(monkeypatch, mock_group_name):
    # If not given, is set to match the clone protocol
    args = {'clone_protocol': "ssh", 'project_name': "test-project",
            'upload_protocol': None, 'repo_type': 'operational', 'cern_id': None}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "ssh://git@gitlab.cern.ch:7999/test-group/test-project.git"


def test_upload_protocol_https(monkeypatch, mock_group_name):
    args = {'clone_protocol': "https", 'project_name': "test-project",
            'upload_protocol': None, 'repo_type': 'operational', 'cern_id': None}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "https://gitlab.cern.ch/test-group/test-project.git"


def test_upload_protocol_ssh(monkeypatch, mock_group_name):
    args = {'clone_protocol': "ssh", 'project_name': "test-project",
            'upload_protocol': None, 'repo_type': 'operational', 'cern_id': None}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "ssh://git@gitlab.cern.ch:7999/test-group/test-project.git"


def test_upload_protocol_kerberos(monkeypatch, mock_group_name):
    args = {'clone_protocol': "kerberos", 'project_name': "test-project",
            'repo_type': 'operational', 'upload_protocol': None, 'cern_id': None}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "https://:@gitlab.cern.ch:8443/test-group/test-project.git"


def test_upload_protocol_wrong(monkeypatch, mock_group_name):
    args = {'clone_protocol': "wrongprotocol", 'upload_protocol': None,
            'project_name': "test-project", 'repo_type': 'operational', 'cern_id': None}
    with pytest.raises(ValueError):
        validation.validate_gitlab(**args)


# #########################
# # Base Path Validation  #
# #########################
def test_validate_base_path_no_dir(tmpdir):
    project_path = os.path.join(tmpdir, "test_project")
    validation.validate_base_path(project_path, "test_project")
    assert not os.path.exists(project_path)


def test_validate_base_path_ask(tmpdir, monkeypatch):
    # Will ask whether to overwrite or not
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        validation.validate_base_path(tmpdir, "test_project")


def test_validate_base_path_say_overwrite(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: "overwrite")
    # if is being said 'overwrite', remove folder
    validation.validate_base_path(tmpdir, "test_project")
    assert not os.path.isdir(project_path)


def test_validate_base_path_not_interactive_passed(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    # Should not ask, directly fail
    with pytest.raises(OSError):
        validation.validate_base_path(tmpdir, "test_project", interactive=False)
    assert os.path.isdir(project_path)


def test_validate_base_path_overwrite_passed(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    # Should not ask, directly overwrite
    validation.validate_base_path(tmpdir, "test_project", overwrite=True)
    assert not os.path.isdir(project_path)


# #########################
# #         Demo          #
# #########################
def test_validate_demo_flag_no_demo_flag_passed(monkeypatch):
    # If --no-demo is passed, the user is not asked anything and validate_demo_flags returns False
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    assert not validation.validate_demo_flags(demo=False, interactive=True)


def test_validate_demo_flag_with_demo_flag_passed(monkeypatch):
    # If --with-demo is passed, the user is not asked anything and validate_demo_flags returns True
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    assert validation.validate_demo_flags(demo=True, interactive=True)


def test_validate_demo_flag_demo_neither_flag_passed(monkeypatch):
    # If no flag is passed, the user is asked what to do
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    with pytest.raises(ZeroDivisionError):
        validation.validate_demo_flags(demo=None, interactive=True)


def test_validate_demo_flag_demo_neither_flag_passed_but_not_interactive_given(monkeypatch):
    # If no flag is passed but --not-interactive is passed, defaults to True without asking the user
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    assert validation.validate_demo_flags(demo=None, interactive=False)


def test_validate_demo_flags_interactive(monkeypatch):
    # Interactive cases
    monkeypatch.setattr('builtins.input', lambda _: "yes")
    assert validation.validate_demo_flags(demo=None, interactive=True)
    monkeypatch.setattr('builtins.input', lambda _: "no")
    assert not validation.validate_demo_flags(demo=None, interactive=True)

