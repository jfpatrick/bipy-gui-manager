import os
import pytest
from argparse import Namespace
import bipy_gui_manager.create_project.create_project as create_project_module
import bipy_gui_manager.create_project.utils as create_project_utils

from .conftest import create_template_files


def create_project_parameters(demo=True, force_demo=True, path=".", name=None, desc=None, author=None, email=None,
                              repo=None, clone_protocol="https", gitlab=True, interactive=True, overwrite=False,
                              template_path=None):
    args = Namespace(
        demo=demo,
        force_demo=force_demo,
        project_path=path,
        project_name=name,
        project_desc=desc,
        project_author=author,
        author_email=email,
        gitlab_repo=repo,
        clone_protocol=clone_protocol,
        gitlab=gitlab,
        interactive=interactive,
        overwrite=overwrite,
        template_path=template_path
    )
    return args


def test_create_project_defaults(monkeypatch):
    # Testing only that it won't fail with the defaults
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information', lambda *a, **k:
        [""]*6 + [parameters])
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.check_path_is_available', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.copy_folder_from_path', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.download_template', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.apply_customizations', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.generate_readme', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.init_local_repo', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.push_first_commit', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.install_project', lambda *a, **k: True)
    create_project_module.create_project(parameters)


def test_create_project_copy_template(monkeypatch):
    # Testing only that it won't fail by taking this option
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git", template_path="here")
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information', lambda *a, **k:
    [""] * 6 + [parameters])
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.check_path_is_available', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.copy_folder_from_path', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.download_template', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.apply_customizations', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.generate_readme', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.init_local_repo', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.push_first_commit', lambda *a, **k: True)
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.install_project', lambda *a, **k: True)
    create_project_module.create_project(parameters)


def test_create_project_handle_errors(monkeypatch):
    # Won't raise this error, will handle it internally
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.gather_setup_information', lambda *a, **k: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.create_project(parameters)


def test_gather_setup_info_most_common_right_values():
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_name_valid():
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.gather_setup_information(parameters)


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


def test_gather_setup_info_gather_setup_info_name_no_not_alphanumeric():
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


def test_name_not_given(monkeypatch):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(desc="A test project", author="Me",
                                           email="m@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    with pytest.raises(ZeroDivisionError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_desc_valid():
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.gather_setup_information(parameters)


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


def test_gather_setup_info_author_valid():
    # Right values
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.gather_setup_information(parameters)


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


def test_gather_setup_info_email_valid():
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.gather_setup_information(parameters)


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


def test_gather_setup_info_repo_https():
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/user/project.git")
    create_project_module.gather_setup_information(parameters)
    # Nested
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/group/subgroup/project.git")
    create_project_module.gather_setup_information(parameters)
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_repo_ssh():
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/user/project.git")
    create_project_module.gather_setup_information(parameters)
    # Nested more than 2
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/group/subgroup/project.git")
    create_project_module.gather_setup_information(parameters)
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="ssh://git@gitlab.cern.ch:7999/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_repo_krb5():
    # Right value
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git")
    create_project_module.gather_setup_information(parameters)
    # Nested more than 2
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/group/subgroup/project.git")
    create_project_module.gather_setup_information(parameters)
    # Too short
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/project.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_repo_no_gitlab_interactive(monkeypatch):
    # Replying 'no-gitlab' in the CLI is allowed
    monkeypatch.setattr('builtins.input', lambda _: 'no-gitlab')
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch")
    create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_repo_no_garbage_address():
    parameters = create_project_parameters(name="test-project", desc="A test", author="Me", email="me@cern.ch",
                                           repo="https://gitlab.cern.ch.git")
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_repo_default_string(monkeypatch):
    # Accept "default" as a gitlab repo value from cli
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="default")
    a, b, c, d, e, gitlab_repo, f = create_project_module.gather_setup_information(parameters)
    assert gitlab_repo == "default"


def test_gather_setup_info_repo_empty_string(monkeypatch):
    # Translate empty string as "default" if given interactively
    monkeypatch.setattr('builtins.input', lambda _: "")
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch")
    a, b, c, d, e, gitlab_repo, f = create_project_module.gather_setup_information(parameters)
    assert gitlab_repo == "default"
    #
    # # Do not accept the empty string from the cli
    # monkeypatch.setattr('builtins.input', lambda _: 1/0)
    # parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
    #                                        email="me@cern.ch", repo="")
    # with pytest.raises(ZeroDivisionError):
    #     create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_repo_not_given(monkeypatch):
    # If not given as parameter will ask
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch")
    with pytest.raises(ZeroDivisionError):
        create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_repo_not_checked_if_gitlab_false():
    # If gitlab=False, repo is not needed
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False)
    create_project_module.gather_setup_information(parameters)
    # If gitlab=False, repo is not checked
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="T0t@l_g@rbage!!&$", gitlab=False)
    create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_no_demo_flag_passed(monkeypatch):
    # If --no-demo is passed, the user is not asked anything and validate_demo_flags returns False
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False, force_demo=False, demo=False)
    a, b, c, d, e, f, new_params = create_project_module.gather_setup_information(parameters)
    assert not new_params.demo
    assert not create_project_utils.validate_demo_flags(force_demo=False, demo=False, interactive=True)


def test_gather_setup_info_with_demo_flag_passed(monkeypatch):
    # If --with-demo is passed, the user is not asked anything and validate_demo_flags returns True
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", gitlab=False, force_demo=True, demo=True)
    a, b, c, d, e, f, new_params = create_project_module.gather_setup_information(parameters)
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
    a, b, c, d, e, f, new_params = create_project_module.gather_setup_information(parameters)
    assert new_params.demo
    assert create_project_utils.validate_demo_flags(force_demo=False, demo=True, interactive=False)


def test_gather_setup_info_not_interactive_all_values_given(monkeypatch):
    # All should go without user input anyways
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git",
                                           interactive=False)
    create_project_module.gather_setup_information(parameters)


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


def test_gather_setup_info_project_path_not_specified(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me",
                                           email="me@cern.ch", repo="https://:@gitlab.cern.ch:8443/user/project.git")
    # Will not ask and default to the local directory
    create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_project_path_specified_and_existing(monkeypatch, tmpdir):
    project_path = os.path.join(tmpdir, "folder_1", "folder_2")
    os.makedirs(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git", path=project_path)
    create_project_module.gather_setup_information(parameters)


def test_gather_setup_info_project_path_not_existing(monkeypatch, tmpdir):
    project_path = os.path.join(tmpdir, "folder_1", "folder_2")
    monkeypatch.setattr('builtins.input', lambda _: 1 / 0)
    parameters = create_project_parameters(name="test-project", desc="A test project", author="Me", email="me@cern.ch",
                                           repo="https://:@gitlab.cern.ch:8443/user/project.git", path=project_path)
    # Wrong path
    with pytest.raises(ValueError):
        create_project_module.gather_setup_information(parameters)



def test_check_path_is_available_no_dir(tmpdir):
    project_path = os.path.join(tmpdir, "test_project")
    create_project_module.check_path_is_available(project_path)
    assert not os.path.exists(project_path)


def test_check_path_is_available_ask(tmpdir, monkeypatch):
    # Will ask whether to overwrite or not
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    with pytest.raises(ZeroDivisionError):
        create_project_module.check_path_is_available(project_path)


def test_check_path_is_available_say_no(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    with open(os.path.join(project_path, "test_file"), "w") as testfile:
        testfile.write("Something")
    monkeypatch.setattr('builtins.input', lambda _: "no")
    # if is being said no, leave folder intact and exit with OSError
    with pytest.raises(OSError):
        create_project_module.check_path_is_available(project_path)
    assert os.path.isdir(project_path)
    assert not os.path.exists(os.path.join(project_path, "be_bi_pyqt_template"))
    assert os.path.exists(os.path.join(project_path, "test_file"))
    with open(os.path.join(project_path, "test_file"), "r") as testfile:
        assert testfile.read() == "Something"


def test_check_path_is_available_say_yes(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: "yes")
    # if is being said yes, remove folder
    create_project_module.check_path_is_available(project_path)
    assert not os.path.isdir(project_path)


def test_check_path_is_available_not_interactive_passed(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    # Should not ask, directly fail
    with pytest.raises(OSError):
        create_project_module.check_path_is_available(project_path, interactive=False)
    assert os.path.isdir(project_path)


def test_check_path_is_available_overwrite_passed(tmpdir, monkeypatch):
    project_path = os.path.join(tmpdir, "test_project")
    os.mkdir(project_path)
    monkeypatch.setattr('builtins.input', lambda _: 1/0)
    # Should not ask, directly overwrite
    create_project_module.check_path_is_available(project_path, overwrite=True)
    assert not os.path.isdir(project_path)


def test_copy_folder_from_path_valid(tmpdir, monkeypatch):
    # Make template folder
    template_folder = os.path.join(tmpdir, "template-folder")
    create_template_files(template_folder, "test-project", True)
    # Ensure it's copied
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.copy_folder_from_path(template_folder, project_path)
    assert os.path.isdir(project_path)
    assert os.path.exists(os.path.join(project_path, "test_project"))
    with open(os.path.join(project_path, "README-template.md"), "r") as testfile:
        assert testfile.read() != ""
    with open(os.path.join(project_path, ".hidden_file"), "r") as testfile:
        assert testfile.read() == "Something hidden"
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as testfile:
        assert testfile.read() != ""
    assert not os.path.exists(os.path.join(project_path, "be_bi_pyqt_template"))


def test_copy_folder_from_path_wrong_template_path(tmpdir, monkeypatch):
    # Ensure an error is raised
    project_path = os.path.join(tmpdir, "test_project")
    with pytest.raises(OSError):
        create_project_module.copy_folder_from_path(os.path.join(tmpdir, "wrong_folder"), project_path)
    assert not os.path.isdir(project_path)


def test_download_template_kerberos_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "kerberos", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_kerberos_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "kerberos", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_ssh_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "ssh", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_ssh_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "ssh", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_https_no_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "https", False)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))


def test_download_template_https_with_demo(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_project_module.download_template(project_path, "https", True)
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    assert os.path.exists(os.path.join(project_path, "test_project", "demo_code.py"))
    with open(os.path.join(project_path, "test_project", "demo_code.py"), "r") as demo:
        assert demo.read() == "raise ValueError('Somebody called this script??')"


def test_download_template_wrong_protocol(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    with pytest.raises(ValueError):
        create_project_module.download_template(project_path, "wrongprotocol", True)
    assert not os.path.isdir(project_path)


def test_apply_customizations_valid_template(tmpdir):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_template_files(project_path, "be-bi-pyqt-template", True)
    assert os.path.isdir(os.path.join(tmpdir, "be-bi-pyqt-template"))
    assert os.path.isdir(os.path.join(tmpdir, "be-bi-pyqt-template", "be_bi_pyqt_template"))

    create_project_module.apply_customizations(project_path=project_path,
                                               project_name="test-project",
                                               project_desc="This is a test",
                                               project_author="Test author",
                                               project_email="test-email@cern.ch")
    assert os.path.isdir(project_path)
    assert os.path.isdir(os.path.join(project_path, "test_project"))
    assert not os.path.exists(os.path.join(project_path, "images"))
    assert os.path.exists(os.path.join(project_path, "README-template.md"))
    with open(os.path.join(project_path, "setup.py"), "r") as setup:
        content = setup.read()
        not_present = [
            "be-bi-pyqt-template",
            "be_bi_pyqt_template",
            "Sara Zanzottera",
            "sara.zanzottera@cern.ch",
            "BE BI PyQt Template",
            "BE BI PyQt Template Code"
        ]
        present = [
            "test-project",
            "Test author",
            "test-email@cern.ch",
            "This is a test",
            "0.0.1.dev1",
            "setup",
            "REQUIREMENTS",
            "pyqt5",
            "pytest",
        ]
        for word in not_present:
            assert word not in content
        for word in present:
            assert word in content


def test_readme(tmpdir):
    project_path = os.path.join(tmpdir, "be-bi-pyqt-template")
    create_template_files(project_path, "be-bi-pyqt-template", True)

    create_project_module.generate_readme(project_path=project_path,
                                          project_name="test-project",
                                          project_desc="This is a test",
                                          project_author="Test author",
                                          project_email="test-email@cern.ch",
                                          gitlab_repo="https://gitlab.cern.ch/test-project.git")

    with open(os.path.join(project_path, "README.md"), "r") as readme:
        content = readme.readlines()
        assert content == [
            "Test Project\n",
            "This is a test\n",
            "test-project\n",
            "test-email@cern.ch\n",
            "Test author\n",
            "https://gitlab.cern.ch/test-project.git\n",
            "Something that does not change"
        ]


def test_git_init_and_push(tmpdir, mock_git):
    project_path = os.path.join(tmpdir, "test-project")
    create_template_files(project_path, "test-project", True)
    create_project_module.init_local_repo(project_path)
    create_project_module.push_first_commit(project_path, "https://gitlab.cern.ch/test-project.git")
