import os
import pytest
import bipy_gui_manager.create_project.create_project as create_project_module
import bipy_gui_manager.create_project.utils as create_project_utils

from .conftest import create_project_parameters


# #########################
# #       General         #
# #########################
def test_gather_setup_info_most_common_right_values():
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.project_name == "test-project"
    assert new_params.project_desc == "A test project"
    assert new_params.project_author == "Me"
    assert new_params.author_email == "me@cern.ch"


# #########################
# #         Name          #
# #########################
def test_gather_setup_info_name_valid():
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.project_name == "test-project"


def test_gather_setup_info_name_not_given_ask(monkeypatch):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(desc="A test project", author="Me",
                                           email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_name_not_given_ask_get_valid(monkeypatch):
    # If given through CLI, should save it
    monkeypatch.setattr('builtins.input', lambda _: "test-project")
    parameters = create_project_parameters(desc="A test project", author="Me",
                                           email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.project_name == "test-project"
    # FIXME Cannot really test that the validation occurs, because it would just keep asking...


def test_gather_setup_info_name_no_underscores():
    # Underscores not allowed
    parameters = create_project_parameters(name="test_project", desc="A test project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_name_no_whitespace():
    # Whitespace not allowed
    parameters = create_project_parameters(name="test project", desc="A test project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_name_no_not_alphanumeric():
    # Non-alphanumeric not allowed
    parameters = create_project_parameters(name="te$t(project)", desc="A test project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_name_no_uppercase():
    # Uppercase not allowed
    parameters = create_project_parameters(name="TestProject", desc="A test project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_name_no_empty_string(monkeypatch):
    # Empty string not allowed - will fail
    monkeypatch.setattr('builtins.input', lambda _: 1/0)  # Just to avoid test hanging if it fails
    parameters = create_project_parameters(name="", desc="A test project", author="Me",
                                           email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


# #########################
# #      Description      #
# #########################
def test_gather_setup_info_desc_valid():
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.project_desc == "A test project"


def test_gather_setup_info_desc_not_given_ask_get_valid(monkeypatch):
    # If given through CLI, should save it
    monkeypatch.setattr('builtins.input', lambda _: "A test project")
    parameters = create_project_parameters(name="test-project", author="Me",
                                           email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.project_desc == "A test project"
    # FIXME Cannot really test that the validation occurs, because it would just keep asking...


def test_gather_setup_info_desc_no_double_quotes():
    # Double quotes not allowed
    parameters = create_project_parameters(name="test-project", desc="A \"test\" project", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_desc_no_empty_string(monkeypatch):
    # Empty string not allowed - will fail
    monkeypatch.setattr('builtins.input', lambda _: 1/0)  # Just to avoid hanging if the test fails
    parameters = create_project_parameters(name="test-project", desc="", author="Me",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_desc_not_given(monkeypatch):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", author="Me", email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.gather_setup_information(parameters)


# #########################
# #        Author         #
# #########################
def test_gather_setup_info_author_valid():
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.project_author == "Me"


def test_gather_setup_info_author_not_given_ask_get_valid(monkeypatch):
    # If given through CLI, should save it
    monkeypatch.setattr('builtins.input', lambda _: "Me")
    parameters = create_project_parameters(name="test-project", desc="A test project",
                                           email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.project_author == "Me"
    # FIXME Cannot really test that the validation occurs, because it would just keep asking...


def test_gather_setup_info_author_no_double_quotes():
    # Duoble quotes not allowed
    parameters = create_project_parameters(name="test-project", desc="A test project", author="M\"e",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_author_no_empty_string(monkeypatch):
    # Empty string not allowed - will fail
    monkeypatch.setattr('builtins.input', lambda _: 1/0)  # Just to avoid hanging if the test breaks
    parameters = create_project_parameters(name="test-project", desc="A test project", author="",
                                           email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_author_not_given(monkeypatch):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.gather_setup_information(parameters)


# #########################
# #        Email          #
# #########################
def test_gather_setup_info_email_valid():
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.author_email == "me@cern.ch"


def test_gather_setup_info_email_not_given_ask_get_valid(monkeypatch):
    # If given through CLI, should save it
    monkeypatch.setattr('builtins.input', lambda _: "me@cern.ch")
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.author_email == "me@cern.ch"
    # FIXME Cannot really test that the validation occurs, because it would just keep asking...


def test_gather_setup_info_email_cern_domain_required():
    # Domain name must be CERN domain
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@email.com",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_email_local_part_is_required(monkeypatch):
    # Local part must be present
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_email_local_part_is_valid(monkeypatch):
    # Local part cannot contain any special char
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="m^)df@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_email_no_empty_string(monkeypatch):
    # Empty string not allowed - will fail
    monkeypatch.setattr('builtins.input', lambda _: 1/0)  #Just to avoid test hanging if it fails
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_email_not_given(monkeypatch):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.gather_setup_information(parameters)


# #########################
# #         Path          #
# #########################
def test_gather_setup_info_project_path_not_specified(monkeypatch, mock_cwd):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="https://:@gitlab.cern.ch:8443/user/project.git")
    # Will not ask and default to the local directory
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.base_path == os.getcwd()


def test_gather_setup_info_project_path_specified_and_existing(monkeypatch, tmpdir):
    project_path = os.path.join(tmpdir, "folder_1", "folder_2")
    os.makedirs(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git", path=project_path)
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.base_path == project_path


def test_gather_setup_info_project_path_not_existing(monkeypatch, tmpdir):
    project_path = os.path.join(tmpdir, "folder_1", "folder_2")
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git", path=project_path)
    # Wrong path
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


# #########################
# #         Demo          #
# #########################
def test_gather_setup_info_no_demo_flag_passed(monkeypatch):
    # If --no-demo is passed, the user is not asked anything and validate_demo_flags returns False
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False, force_demo=False, demo=False)
    new_params = create_project_module.gather_setup_information(parameters)
    assert not new_params.demo
    assert not create_project_utils.validate_demo_flags(force_demo=False, demo=False, interactive=True)


def test_gather_setup_info_with_demo_flag_passed(monkeypatch):
    # If --with-demo is passed, the user is not asked anything and validate_demo_flags returns True
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False, force_demo=True, demo=True)
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.demo
    assert create_project_utils.validate_demo_flags(force_demo=True, demo=True, interactive=True)


def test_gather_setup_info_demo_neither_flag_passed(monkeypatch):
    # If no flag is passed, the user is asked what to do
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False, force_demo=False, demo=True)
    with pytest.raises(ZeroDivisionError):
        create_project_module.gather_setup_information(parameters)
    with pytest.raises(ZeroDivisionError):
        create_project_utils.validate_demo_flags(force_demo=False, demo=True, interactive=True)


def test_gather_setup_info_demo_neither_flag_passed_but_not_interactive_given(monkeypatch):
    # If no flag is passed but --not-interactive is passed, defaults to True without asking the user
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           gitlab=False, force_demo=False, demo=True, interactive=False)
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.demo
    assert create_project_utils.validate_demo_flags(force_demo=False, demo=True, interactive=False)


# #########################
# #    Not Interactive    #
# #########################
def test_gather_setup_info_not_interactive_all_values_given(monkeypatch):
    # All should go without user input anyways
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git")
    new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.interactive
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git",
                                           interactive=False)
    new_params = create_project_module.gather_setup_information(parameters)
    assert not new_params.interactive


def test_gather_setup_info_not_interactive_not_all_values_given(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", interactive=False)
    # Will not ask (ZeroDivisionError) but rather fail (ValueError)
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_not_interactive_values_given_wrong(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="what shall I put here?!?", interactive=False)
    # Will not ask (ZeroDivisionError) but rather fail (ValueError)
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)

