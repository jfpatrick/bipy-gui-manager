import pytest
import bipy_gui_manager.create_project.utils as create_project_utils

from .conftest import create_project_parameters


# #########################
# #    Valid Explicit     #
# #########################
def test_gather_setup_info_repo_https():
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/user/project.git")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "https://gitlab.cern.ch/user/project.git"
    # Nested
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/group/subgroup/project.git")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "https://gitlab.cern.ch/group/subgroup/project.git"
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/project.git")
    with pytest.raises(ValueError):
        create_project_utils.validate_gitlab(parameters)


def test_gather_setup_info_repo_ssh():
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "ssh://git@gitlab.cern.ch:7999/user/project.git"
    # Nested more than 2
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/group/subgroup/project.git")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "ssh://git@gitlab.cern.ch:7999/group/subgroup/project.git"
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/project.git")
    with pytest.raises(ValueError):
        create_project_utils.validate_gitlab(parameters)


def test_gather_setup_info_repo_krb5():
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "https://:@gitlab.cern.ch:8443/user/project.git"
    # Nested more than 2
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/group/subgroup/project.git")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "https://:@gitlab.cern.ch:8443/group/subgroup/project.git"
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/project.git")
    with pytest.raises(ValueError):
        create_project_utils.validate_gitlab(parameters)


# #########################
# #   Missing or Wrong    #
# #########################
def test_gather_setup_info_repo_no_gitlab(monkeypatch):
    # Replying 'no-gitlab' in the CLI is allowed
    monkeypatch.setattr('builtins.input', lambda _: 'no-gitlab')
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           gitlab=False)
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo is None


def test_gather_setup_info_repo_no_gitlab_interactive(monkeypatch):
    # Replying 'no-gitlab' in the CLI is allowed
    monkeypatch.setattr('builtins.input', lambda _: 'no-gitlab')
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo is None
    
    
def test_gather_setup_info_repo_no_garbage_address():
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch.git")
    with pytest.raises(ValueError):
        create_project_utils.validate_gitlab(parameters)


def test_gather_setup_info_repo_empty_string(monkeypatch):
    # Translate empty string as "default" if given interactively
    monkeypatch.setattr('bipy_gui_manager.create_project.utils.GROUP_NAME', 'test-group')
    monkeypatch.setattr('builtins.input', lambda _: "")
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "https://gitlab.cern.ch/test-group/test-project.git"

    # Translate empty string as "default" in the CLI
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "https://gitlab.cern.ch/test-group/test-project.git"


def test_gather_setup_info_repo_not_given(monkeypatch):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch")
    with pytest.raises(ZeroDivisionError):
        create_project_utils.validate_gitlab(parameters)


def test_gather_setup_info_repo_not_given_ask(monkeypatch):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: "https://gitlab.cern.ch/test-group/test-project.git")
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "https://gitlab.cern.ch/test-group/test-project.git"

    monkeypatch.setattr('builtins.input', lambda _: "no-gitlab")
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo is None


def test_gather_setup_info_repo_not_checked_if_gitlab_false():
    # If gitlab=False, repo is not needed
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False)
    create_project_utils.validate_gitlab(parameters)
    
    # TODO If gitlab=False but repo is defined, throw exception
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="T0t@l_g@rbage!!&$", gitlab=False)
    create_project_utils.validate_gitlab(parameters)


# #########################
# #    Upload Protocol    #
# #########################
def upload_protocol_not_given(monkeypatch):
    # If not given, is set to match the clone protocol
    monkeypatch.setattr('bipy_gui_manager.create_project.utils.GROUP_NAME', 'test-group')
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="default", clone_protocol="ssh")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.upload_protocol == "ssh"
    assert new_params.gitlab_repo == "ssh://git@gitlab.cern.ch:7999/test-group/test-project.git"


def upload_protocol_https(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.utils.GROUP_NAME', 'test-group')
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="default", upload_protocol="https")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.upload_protocol == "https"
    assert new_params.gitlab_repo == "https://gitlab.cern.ch/test-group/test-project.git"


def upload_protocol_ssh(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.utils.GROUP_NAME', 'test-group')
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="default", upload_protocol="ssh")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.upload_protocol == "ssh"
    assert new_params.gitlab_repo == "ssh://git@gitlab.cern.ch:7999/test-group/test-project.git"


def upload_protocol_kerberos(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.utils.GROUP_NAME', 'test-group')
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="default", upload_protocol="kerberos")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.upload_protocol == "kerberos"
    assert new_params.gitlab_repo == "https://:@gitlab.cern.ch:8443/test-group/test-project.git"


def upload_protocol_wrong(monkeypatch):
    monkeypatch.setattr('bipy_gui_manager.create_project.utils.GROUP_NAME', 'test-group')
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="default", upload_protocol="myprotocol")
    with pytest.raises(ValueError):
        create_project_utils.validate_gitlab(parameters)


# #########################
# #  Default Resolution   #
# #########################
def test_gather_setup_info_repo_default(monkeypatch):
    # Accept "default" as a gitlab repo value from cli
    monkeypatch.setattr('bipy_gui_manager.create_project.utils.GROUP_NAME', 'test-group')
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="default")
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.gitlab_repo == "https://gitlab.cern.ch/test-group/test-project.git"
    
    
def test_gather_setup_info_repo_default_ensure_create_repo_is_set(monkeypatch):
    # Accept "default" as a gitlab repo value from cli
    monkeypatch.setattr('bipy_gui_manager.create_project.utils.GROUP_NAME', 'test-group')
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="default", create_repo=None)
    new_params = create_project_utils.validate_gitlab(parameters)
    assert new_params.create_repo

    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="https://gitlab.cern.ch/test-group/test-project.git", 
                                           create_repo=None)
    new_params = create_project_utils.validate_gitlab(parameters)
    assert not new_params.create_repo

