import os
import pytest
from bipy_gui_manager.create_project import validation
from .conftest import create_project_parameters


def test_validate_or_fail():
    # Value is valid
    assert "test value" == validation.validate_or_fail("test value", lambda v: "test" in v, "neg test feedback")
    # Value is not valid
    with pytest.raises(ValueError):
        validation.validate_or_fail("test value", lambda v: "test" not in v, "neg test feedback")


def test_validate_or_ask(monkeypatch):
    # Valid value
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    assert "test value" == validation.validate_or_ask(lambda v: "test" in v, "Test question", "test Neg Feedback",
                                                      start_value="test value")
    # Not valid value - ask
    monkeypatch.setattr('builtins.input', lambda _: "valid value")
    assert "valid value" == validation.validate_or_ask(lambda v: "test" not in v, "Test question", "test Neg Feedback",
                                                       start_value="test value")

    # No value - ask
    monkeypatch.setattr('builtins.input', lambda _: "test value")
    assert "test value" == validation.validate_or_ask(lambda v: "test" in v, "Test question", "test Neg Feedback")


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
# #       GitLab Repo     #
# #########################
# def test_validate_gitlab_repo_operational(monkeypatch):
#     args = {'gitlab': True, 'interactive': True, 'upload_protocol': "https", 'clone_protocol': "https",
#             'project_name': "test-project", 'repo': 'operational'}
#     # Replying 'operational' in the repo flag translates into an URL under 'bisw-python'
#     # TODO
#     new_params = validation.validate_gitlab(**args)
#
#
# def test_validate_gitlab_repo_test(monkeypatch):
#     args = {'gitlab': True, 'interactive': True, 'upload_protocol': "https", 'clone_protocol': "https",
#             'project_name': "test-project", 'repo': 'operational'}
#     # Replying 'test' in the repo flag translates into an URL under the user's personal space
#     # TODO
#     new_params = validation.validate_gitlab(**args)
#
#
# def test_validate_gitlab_repo_no_gitlab_not_allowed(monkeypatch):
#     args = {'gitlab': True, 'interactive': True, 'upload_protocol': "https", 'clone_protocol': "https",
#             'project_name': "test-project", 'repo': 'no-gitlab'}
#     # Replying 'no-gitlab' in the repo flag is not allowed
#     with pytest.raises(ValueError):
#         validation.validate_gitlab(**args)
#
#
# def test_validate_gitlab_repo_no_gitlab_interactive(monkeypatch):
#     args = {'gitlab': True, 'interactive': True, 'upload_protocol': "https", 'clone_protocol': "https",
#             'project_name': "test-project", 'repo': None}
#     # Replying 'no-gitlab' interactively is not allowed
#     monkeypatch.setattr('builtins.input', lambda _: 'no-gitlab')
#     with pytest.raises(ValueError):
#         validation.validate_gitlab(**args)
#
#
# def test_validate_gitlab_repo_operational_interactive(monkeypatch):
#     args = {'gitlab': True, 'interactive': True, 'upload_protocol': "https", 'clone_protocol': "https",
#             'project_name': "test-project", 'repo': None}
#     # Replying 'operational' interactively is allowed
#     # TODO
#     monkeypatch.setattr('builtins.input', lambda _: 'operational')
#     new_params = validation.validate_gitlab(**args)
#
#
# def test_validate_gitlab_repo_test_interactive(monkeypatch):
#     args = {'gitlab': True, 'interactive': True, 'upload_protocol': "https", 'clone_protocol': "https",
#             'project_name': "test-project", 'repo': None}
#     # Replying 'test' interactively is allowed
#     # TODO
#     monkeypatch.setattr('builtins.input', lambda _: 'test')
#     new_params = validation.validate_gitlab(**args)
#
#
# def test_validate_gitlab_repo_empty_string_interactive_not_allowed(monkeypatch):
#     args = {'gitlab': True, 'interactive': True, 'upload_protocol': "https", 'clone_protocol': "https",
#             'project_name': "test-project", 'repo': None}
#     # Translate empty string as "default" if given interactively
#     monkeypatch.setattr('bipy_gui_manager.create_project.validation.GROUP_NAME', 'test-group')
#     monkeypatch.setattr('builtins.input', lambda _: "")
#     with pytest.raises(ValueError):
#         validation.validate_gitlab(**args)
#
#
# def test_validate_gitlab_repo_not_given(monkeypatch):
#     args = {'gitlab': True, 'interactive': True, 'upload_protocol': "https", 'clone_protocol': "https",
#             'project_name': "test-project", 'repo': None}
#     # If not given as parameter will ask
#     monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
#     with pytest.raises(ZeroDivisionError):
#         validation.validate_gitlab(**args)


def test_validate_gitlab_repo_not_checked_if_gitlab_false():
    # If gitlab=False, repo is not needed
    args = {'gitlab': False, 'upload_protocol': "https", 'clone_protocol': "https",
            'project_name': "test-project", 'repo_type': 'operational', 'cern_id': 'me'}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url is None



# #########################
# #    Upload Protocol    #
# #########################
def upload_protocol_not_given(monkeypatch):
    # If not given, is set to match the clone protocol
    monkeypatch.setattr('bipy_gui_manager.create_project.GROUP_NAME', 'test-group')
    args = {'gitlab': True, 'interactive': True, 'clone_protocol': "ssh", 'project_name': "test-project",
            'upload_protocol': None, 'repo_type': 'operational'}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "ssh://git@gitlab.cern.ch:7999/test-group/test-project.git"


def upload_protocol_https(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.GROUP_NAME', 'test-group')
    args = {'gitlab': True, 'interactive': True, 'clone_protocol': "https", 'project_name': "test-project",
            'upload_protocol': None, 'repo_type': 'operational'}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "https://gitlab.cern.ch/test-group/test-project.git"


def upload_protocol_ssh(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.GROUP_NAME', 'test-group')
    args = {'gitlab': True, 'interactive': True, 'clone_protocol': "ssh", 'project_name': "test-project",
            'upload_protocol': None, 'repo_type': 'operational'}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "ssh://git@gitlab.cern.ch:7999/test-group/test-project.git"


def upload_protocol_kerberos(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.GROUP_NAME', 'test-group')
    args = {'gitlab': True, 'interactive': True, 'clone_protocol': "kerberos", 'project_name': "test-project",
            'repo_type': 'operational', 'upload_protocol': None}
    repo_url = validation.validate_gitlab(**args)
    assert repo_url == "https://:@gitlab.cern.ch:8443/test-group/test-project.git"

def upload_protocol_wrong(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.GROUP_NAME', 'test-group')
    args = {'gitlab': True, 'interactive': True, 'clone_protocol': "wrongprotocol", 'upload_protocol': None,
            'project_name': "test-project", 'repo_type': 'operational'}
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
    assert not validation.validate_demo_flags(force_demo=False, demo=False, interactive=True)


def test_validate_demo_flag_with_demo_flag_passed(monkeypatch):
    # If --with-demo is passed, the user is not asked anything and validate_demo_flags returns True
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    assert validation.validate_demo_flags(force_demo=True, demo=True, interactive=True)


def test_validate_demo_flag_demo_neither_flag_passed(monkeypatch):
    # If no flag is passed, the user is asked what to do
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    with pytest.raises(ZeroDivisionError):
        validation.validate_demo_flags(force_demo=False, demo=True, interactive=True)


def test_validate_demo_flag_demo_neither_flag_passed_but_not_interactive_given(monkeypatch):
    # If no flag is passed but --not-interactive is passed, defaults to True without asking the user
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    assert validation.validate_demo_flags(force_demo=False, demo=True, interactive=False)


def test_validate_demo_flags_interactive(monkeypatch):
    # Interactive cases
    monkeypatch.setattr('builtins.input', lambda _: "yes")
    assert validation.validate_demo_flags(force_demo=False, demo=True, interactive=True)
    monkeypatch.setattr('builtins.input', lambda _: "no")
    assert not validation.validate_demo_flags(force_demo=False, demo=True, interactive=True)

