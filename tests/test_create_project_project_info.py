import os
import pytest
from bipy_gui_manager.create_project import project_info

from .conftest import create_project_parameters


# #########################
# #       General         #
# #########################
def test_collect_most_common_right_values(mock_phonebook):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    new_params = project_info.collect(parameters)
    assert new_params["project_name"] == "test-project"
    assert new_params["project_desc"] == "A test project"
    assert new_params["author_cern_id"] == "me"
    assert new_params["author_full_name"] == "Test User"
    assert new_params["author_email"] == "test.email@cern.ch"


# #########################
# #         Name          #
# #########################
def test_collect_name_valid(mock_phonebook):
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    new_params = project_info.collect(parameters)
    assert new_params["project_name"] == "test-project"


def test_collect_name_not_given_ask(monkeypatch, mock_phonebook):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_name_not_given_ask_get_valid(monkeypatch, mock_phonebook):
    # If given through CLI, should save it
    monkeypatch.setattr('builtins.input', lambda _: "test-project")
    parameters = create_project_parameters(desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = project_info.collect(parameters)
    assert new_params["project_name"] == "test-project"
    # FIXME Cannot really test that the validation occurs, because it would just keep asking...


def test_collect_name_no_underscores(mock_phonebook):
    # Underscores not allowed
    parameters = create_project_parameters(name="test_project", desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_name_no_whitespace(mock_phonebook):
    # Whitespace not allowed
    parameters = create_project_parameters(name="test project", desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_name_no_not_alphanumeric(mock_phonebook):
    # Non-alphanumeric not allowed
    parameters = create_project_parameters(name="te$t(project)", desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_name_no_uppercase(mock_phonebook):
    # Uppercase not allowed
    parameters = create_project_parameters(name="TestProject", desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_name_no_empty_string(monkeypatch, mock_phonebook):
    # Empty string not allowed - will fail
    monkeypatch.setattr('builtins.input', lambda _: 1/0)  # Just to avoid test hanging if it fails
    parameters = create_project_parameters(name="", desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


# #########################
# #      Description      #
# #########################
def test_collect_desc_valid(mock_phonebook):
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    new_params = project_info.collect(parameters)
    assert new_params["project_desc"] == "A test project"


def test_collect_desc_not_given_ask_get_valid(monkeypatch, mock_phonebook):
    # If given through CLI, should save it
    monkeypatch.setattr('builtins.input', lambda _: str("A test project"))
    parameters = create_project_parameters(name="test-project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = project_info.collect(parameters)
    assert new_params["project_desc"] == "A test project"
    # FIXME Cannot really test that the validation occurs, because it would just keep asking...


def test_collect_desc_no_double_quotes(mock_phonebook):
    # Double quotes not allowed
    parameters = create_project_parameters(name="test-project", desc="A \"test\" project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_desc_no_empty_string(monkeypatch, mock_phonebook):
    # Empty string not allowed - will fail
    monkeypatch.setattr('builtins.input', lambda _: 1/0)  # Just to avoid hanging if the test fails
    parameters = create_project_parameters(name="test-project", desc="", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_desc_not_given(monkeypatch, mock_phonebook):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", author="me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git",
                                           interactive=False)
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


# #########################
# #         Path          #
# #########################
def test_collect_project_path_use_base_path_validation(monkeypatch, mock_cwd, mock_phonebook):
    monkeypatch.setattr('bipy_gui_manager.create_project.validation.validate_base_path', lambda *a, **k: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path="",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git")
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_project_path_empty_string(monkeypatch, mock_cwd, mock_phonebook):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path="",
                                            repo="https://:@gitlab.cern.ch:8443/user/project.git")
    # Empty string is valid, means "current directory"
    new_params = project_info.collect(parameters)
    assert new_params["base_path"] == ""


def test_collect_project_path_not_specified(monkeypatch, mock_cwd, mock_phonebook):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=None,
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git")
    # Will ask
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_project_path_specified_and_existing(monkeypatch, tmpdir, mock_phonebook):
    project_path = os.path.join(tmpdir, "folder_1", "folder_2")
    os.makedirs(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git", path=project_path)
    new_params = project_info.collect(parameters)
    assert new_params["base_path"] == project_path


def test_collect_project_path_specified_not_existing(monkeypatch, tmpdir, mock_phonebook):
    # Such path will be created
    # NOTE might still fail due to permissions, but we don't account for that.
    project_path = os.path.join(tmpdir, "folder_1", "folder_2")
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git", path=project_path)
    new_params = project_info.collect(parameters)
    assert new_params["base_path"] == project_path


# #########################
# #    Not Interactive    #
# #########################
def test_collect_not_interactive_all_values_given(monkeypatch, mock_phonebook):
    # All must go without user input
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git")
    assert parameters.interactive
    project_info.collect(parameters)

    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", 
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git",
                                           interactive=False)
    assert not parameters.interactive
    project_info.collect(parameters)


def test_collect_not_interactive_not_all_values_given(monkeypatch, mock_phonebook):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", interactive=False)
    # Will not ask (ZeroDivisionError) but rather fail (ValueError)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_not_interactive_values_given_wrong(monkeypatch, mock_phonebook):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                            repo="what shall I put here?!?", interactive=False)
    # Will not ask (ZeroDivisionError) but rather fail (ValueError)
    with pytest.raises(ValueError):
        project_info.collect(parameters)

