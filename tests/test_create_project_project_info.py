import os
import pytest
from bipy_gui_manager.create_project import project_info

from .conftest import create_project_parameters


# #########################
# #       General         #
# #########################
def test_collect_most_common_right_values(mock_phonebook, tmpdir):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", interactive=False, gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["project_name"] == "test-project"
    assert new_params["project_desc"] == "A test project"
    assert new_params["author_cern_id"] == "me"
    assert new_params["author_full_name"] == "Test User"
    assert new_params["author_email"] == "test.email@cern.ch"
    assert new_params["author_token"] == "private_token=skip-authentication"


# #########################
# #  Author Credentials   #
# #########################
def test_collect_credentials_cernid_given(mock_phonebook, tmpdir):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["author_cern_id"] == "me"
    assert new_params["author_full_name"] == "Test User"
    assert new_params["author_email"] == "test.email@cern.ch"


def test_collect_credentials_cernid_discovered(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('getpass.getuser', lambda: "me")
    parameters = create_project_parameters(name="test-project", desc="A test project", path=tmpdir,
                                           repo_type="test", gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["author_cern_id"] == "me"
    assert new_params["author_full_name"] == "Test User"
    assert new_params["author_email"] == "test.email@cern.ch"


def test_collect_credentials_cernid_given_wrong(monkeypatch, mock_phonebook, tmpdir):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="you", interactive=False,
                                           repo_type="test", gitlab_token="skip-authentication", path=tmpdir)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_credentials_cernid_discovered_wrong(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('getpass.getuser', lambda: "you")
    parameters = create_project_parameters(name="test-project", desc="A test project", interactive=False, path=tmpdir,
                                           repo_type="test", gitlab_token="skip-authentication")
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_credentials_cernid_missing_ask(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('getpass.getuser', lambda: None)
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", path=tmpdir,
                                           repo_type="test", gitlab_token="skip-authentication")
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_credentials_cernid_ask_process_input(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('getpass.getuser', lambda: "")
    monkeypatch.setattr('builtins.input', lambda _: "me")
    parameters = create_project_parameters(name="test-project", desc="A test project", path=tmpdir,
                                           repo_type="test", gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["author_cern_id"] == "me"
    assert new_params["author_full_name"] == "Test User"
    assert new_params["author_email"] == "test.email@cern.ch"


# #########################
# #         Name          #
# #########################
def test_collect_name_valid(mock_phonebook, tmpdir):
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", interactive=False, gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["project_name"] == "test-project"


def test_collect_name_not_given_ask(monkeypatch, mock_phonebook, tmpdir):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(desc="A test project", author="me", repo_type="test", path=tmpdir,
                                           gitlab_token="skip-authentication")
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_name_not_given_ask_get_valid(monkeypatch, mock_phonebook, tmpdir):
    # If given through CLI, should save it
    monkeypatch.setattr('builtins.input', lambda _: "test-project")
    parameters = create_project_parameters(desc="A test project", author="me", repo_type="test", path=tmpdir,
                                           gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["project_name"] == "test-project"


def test_collect_name_no_underscores(mock_phonebook, tmpdir):
    # Underscores not allowed
    parameters = create_project_parameters(name="test_project", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", interactive=False, gitlab_token="skip-authentication")
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_name_no_whitespace(mock_phonebook, tmpdir):
    # Whitespace not allowed
    parameters = create_project_parameters(name="test project", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", interactive=False, gitlab_token="skip-authentication")
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_name_no_not_alphanumeric(mock_phonebook, tmpdir):
    # Non-alphanumeric not allowed
    parameters = create_project_parameters(name="te$t(project)", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", interactive=False, gitlab_token="skip-authentication")
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_name_no_uppercase(mock_phonebook, tmpdir):
    # Uppercase not allowed
    parameters = create_project_parameters(name="TestProject", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", interactive=False, gitlab_token="skip-authentication")
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_name_no_empty_string(monkeypatch, mock_phonebook, tmpdir):
    # Empty string not allowed
    parameters = create_project_parameters(name="", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", interactive=False, gitlab_token="skip-authentication")
    with pytest.raises(ValueError):
        project_info.collect(parameters)


# #########################
# #      Description      #
# #########################
def test_collect_desc_valid(mock_phonebook, tmpdir):
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", repo_type="test",
                                           gitlab_token="skip-authentication", path=tmpdir)
    new_params = project_info.collect(parameters)
    assert new_params["project_desc"] == "A test project"


def test_collect_desc_not_given_ask(monkeypatch, mock_phonebook, tmpdir):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", author="me", repo_type="test", path=tmpdir,
                                           gitlab_token="skip-authentication")
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_desc_not_given_ask_get_valid(monkeypatch, mock_phonebook, tmpdir):
    # If given through CLI, should save it
    monkeypatch.setattr('builtins.input', lambda _: "A test project")
    parameters = create_project_parameters(name="test-project", author="me", repo_type="test", path=tmpdir,
                                           gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["project_desc"] == "A test project"


def test_collect_desc_no_double_quotes(mock_phonebook, tmpdir):
    # Double quotes not allowed
    parameters = create_project_parameters(name="test-project", desc="A \"test\" project", author="me", path=tmpdir,
                                           repo_type="test", interactive=False, gitlab_token="skip-authentication")
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_desc_no_empty_string(monkeypatch, mock_phonebook, tmpdir):
    # Empty string not allowed
    parameters = create_project_parameters(name="test-project", desc="", author="me", repo_type="test", path=tmpdir,
                                           gitlab_token="skip-authentication", interactive=False)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


# #########################
# #         Path          #
# #########################
def test_collect_project_path_specified_exists(monkeypatch, tmpdir, mock_phonebook):
    # Right value passed
    project_path = os.path.join(tmpdir, "folder_1", "folder_2")
    os.makedirs(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo_type="test", path=project_path, gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["base_path"] == project_path


def test_collect_project_path_specified_not_existing(monkeypatch, tmpdir, mock_phonebook):
    # Such path will be created
    # NOTE might still fail due to permissions, but we don't account for that.
    project_path = os.path.join(tmpdir, "folder_1", "folder_2")
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo_type="test", path=project_path, gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["base_path"] == project_path


def test_collect_project_path_empty_string(monkeypatch, mock_cwd, mock_phonebook, tmpdir):
    # Empty string is valid, means "current directory"
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    os.chdir(tmpdir)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path="",
                                           repo_type="test", gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["base_path"] == ""


def test_collect_project_path_not_specified(monkeypatch, mock_cwd, mock_phonebook):
    # If path is not given will ask
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=None,
                                           repo_type="test", gitlab_token="skip-authentication")
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_project_path_contains_folder_named_as_project(monkeypatch, tmpdir, mock_phonebook):
    # Ask what to do - overwrite or enter new path
    existing_path = os.path.join(tmpdir, "folder_1", "test-project")
    os.makedirs(existing_path)
    project_path = os.path.join(tmpdir, "folder_1")
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo_type="test", path=project_path, gitlab_token="skip-authentication")
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_project_path_contains_folder_named_as_project_overwrite(monkeypatch, tmpdir, mock_phonebook):
    # Accepts the path and deletes the conflicting folder
    existing_path = os.path.join(tmpdir, "folder_1", "test-project")
    os.makedirs(existing_path)
    project_path = os.path.join(tmpdir, "folder_1")
    monkeypatch.setattr('builtins.input', lambda _: "overwrite")
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",
                                           repo_type="test", path=project_path, gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["base_path"] == project_path
    assert not os.path.isdir(existing_path)


# #########################
# #      Repo Type        #
# #########################
def test_collect_repo_type_operational(monkeypatch, mock_phonebook, tmpdir):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", interactive=False,
                                           repo_type="operational", gitlab_token="skip-authentication", path=tmpdir)
    new_params = project_info.collect(parameters)
    assert new_params["repo_type"] == "operational"


def test_collect_repo_type_test(monkeypatch, mock_phonebook, tmpdir):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", interactive=False,
                                           repo_type="test", gitlab_token="skip-authentication",  path=tmpdir)
    new_params = project_info.collect(parameters)
    assert new_params["repo_type"] == "test"


def test_collect_repo_type_wrong(monkeypatch, mock_phonebook, tmpdir):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", interactive=False,
                                           repo_type="wrong", gitlab_token="skip-authentication", path=tmpdir)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_repo_type_missing(monkeypatch, mock_phonebook, tmpdir):
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           interactive=False, gitlab_token="skip-authentication")
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_repo_type_missing_ask(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           gitlab_token="skip-authentication")
    with pytest.raises(ZeroDivisionError):
        project_info.collect(parameters)


def test_collect_repo_type_missing_ask_process_input(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('builtins.input', lambda _: "test")
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           gitlab_token="skip-authentication")
    new_params = project_info.collect(parameters)
    assert new_params["repo_type"] == "test"


def test_collect_repo_type_no_gitlab(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('builtins.input', lambda _: "test")
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           gitlab=False)
    new_params = project_info.collect(parameters)
    assert "repo_type" not in new_params


# #########################
# #    Not Interactive    #
# #########################
def test_collect_not_interactive_all_values_given(monkeypatch, mock_phonebook, tmpdir):
    # All must go without user input in both cases
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           repo_type="test", gitlab_token="skip-authentication")
    assert parameters.interactive
    project_info.collect(parameters)

    parameters = create_project_parameters(name="test-project", desc="A test project", author="me",  path=tmpdir,
                                           repo_type="test", gitlab_token="skip-authentication", interactive=False)
    assert not parameters.interactive
    project_info.collect(parameters)


def test_collect_not_interactive_not_all_values_given(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", interactive=False,
                                           gitlab_token="skip-authentication", path=tmpdir)
    # Will not ask (ZeroDivisionError) but rather fail (ValueError)
    with pytest.raises(ValueError):
        project_info.collect(parameters)


def test_collect_not_interactive_values_given_wrong(monkeypatch, mock_phonebook, tmpdir):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="me", path=tmpdir,
                                           repo_type="what shall I put here?!?", interactive=False,
                                           gitlab_token="skip-authentication")
    # Will not ask (ZeroDivisionError) but rather fail (ValueError)
    with pytest.raises(ValueError):
        project_info.collect(parameters)

