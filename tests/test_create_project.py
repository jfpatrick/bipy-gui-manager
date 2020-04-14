import pytest
import mock
from argparse import Namespace
import be_bi_pyqt_project_manager
import be_bi_pyqt_project_manager.create_project as create_project_module


@pytest.fixture
def raise_on_input():
    be_bi_pyqt_project_manager.create_project.input = lambda: 1/0
    yield
    be_bi_pyqt_project_manager.create_project.input = input


def create_project_parameters(demo=True, name=None, desc=None, author=None, email=None, repo=None,
                              clone_protocol="https", gitlab=True, template_path=None):
    args = Namespace(
        demo=demo,
        project_name=name,
        project_desc=desc,
        project_author=author,
        author_email=email,
        gitlab_repo=repo,
        clone_protocol=clone_protocol,
        gitlab=gitlab,
        template_path=template_path
    )
    return args


def mock_all_subtasks():
    create_project_module.download_template = lambda *args, **kwargs: True
    create_project_module.create_directories = lambda *args, **kwargs: True
    create_project_module.apply_customizations = lambda *args, **kwargs: True
    create_project_module.generate_readme = lambda *args, **kwargs: True
    create_project_module.push_first_commit = lambda *args, **kwargs: True
    create_project_module.install_project = lambda *args, **kwargs: True


def test_create_project_main_function_most_common_right_values():
    mock_all_subtasks()
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_create_project_main_function_name_valid():
    mock_all_subtasks()
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)

def test_create_project_main_function_name_no_underscores():
    mock_all_subtasks()
    # Underscores not allowed
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test_project", desc="A test project", author="Me",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_name_no_whitespace():
    mock_all_subtasks()
    # Whitespace not allowed
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test project", desc="A test project", author="Me",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_name_no_not_alphanumeric():
    mock_all_subtasks()
    # Non-alphanumeric not allowed
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="te$t(project)", desc="A test project", author="Me",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_name_no_uppercase():
    mock_all_subtasks()
    # Uppercase not allowed
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="TestProject", desc="A test project", author="Me",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_name_no_empty_string(monkeypatch):
    mock_all_subtasks()
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="", desc="A test project", author="Me",
                                               email="m@cern.ch",
                                               repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_name_not_given(monkeypatch):
    mock_all_subtasks()
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(desc="A test project", author="Me",
                                               email="m@cern.ch",
                                               repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)


def test_create_project_main_function_desc_valid():
    mock_all_subtasks()
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_create_project_main_function_desc_no_double_quotes():
    mock_all_subtasks()
    # Duoble quotes not allowed
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A \"test\" project", author="Me",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)


def test_create_project_main_function_desc_no_empty_string(monkeypatch):
    mock_all_subtasks()
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="test-project", desc="", author="Me",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)


def test_create_project_main_function_desc_not_given(monkeypatch):
    mock_all_subtasks()
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="test-project", author="Me", email="m@cern.ch",
                                               repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)


def test_create_project_main_function_author_valid():
    mock_all_subtasks()
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_create_project_main_function_author_no_double_quotes():
    mock_all_subtasks()
    # Duoble quotes not allowed
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A test project", author="M\"e",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)


def test_create_project_main_function_author_no_empty_string(monkeypatch):
    mock_all_subtasks()
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="test-project", desc="A test project", author="",
                                               email="m@cern.ch", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)


def test_create_project_main_function_author_not_given(monkeypatch):
    mock_all_subtasks()
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="test-project", desc="A test project", email="m@cern.ch",
                                               repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)


def test_create_project_main_function_email_valid():
    mock_all_subtasks()
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)

def test_create_project_main_function_email_cern_domain_required():
    mock_all_subtasks()
    # Domain name must be CERN domain
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@email.com",
                                               repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_email_local_part_is_required(monkeypatch):
    mock_all_subtasks()
    # Local part must be present
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="@cern.ch",
                                               repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_email_local_part_is_valid(monkeypatch):
    mock_all_subtasks()
    # Local part cannot contain any special char
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="m^)df@cern.ch",
                                               repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_email_no_empty_string(monkeypatch):
    mock_all_subtasks()
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                               email="", repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_email_not_given(monkeypatch):
    mock_all_subtasks()
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                               repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
        create_project_module.create_project(parameters)


def test_create_project_main_function_repo_https():
    mock_all_subtasks()
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/user/project.git")
    create_project_module.create_project(parameters)
    # Nested
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/group/subgroup/project.git")
    create_project_module.create_project(parameters)
    # Too short
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                               repo="https://gitlab.cern.ch/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_repo_ssh():
    mock_all_subtasks()
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)
    # Nested more than 2
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/group/subgroup/project.git")
    create_project_module.create_project(parameters)
    # Too short
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                               repo="ssh://git@gitlab.cern.ch:7999/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_repo_krb5():
    mock_all_subtasks()
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git")
    create_project_module.create_project(parameters)
    # Nested more than 2
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/group/subgroup/project.git")
    create_project_module.create_project(parameters)
    # Too short
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                               repo="https://:@gitlab.cern.ch:8443/project.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_repo_no_garbage_address():
    mock_all_subtasks()
    with pytest.raises(ValueError):
        parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                               repo="https://gitlab.cern.ch.git")
        create_project_module.create_project(parameters)

def test_create_project_main_function_repo_no_empty_string(monkeypatch):
    mock_all_subtasks()
    # Empty string not allowed - will treat as None and ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                               email="me@cern.ch", repo="")
        create_project_module.create_project(parameters)

def test_create_project_main_function_repo_not_given(monkeypatch):
    mock_all_subtasks()
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                               email="me@cern.ch")
        create_project_module.create_project(parameters)

