import pytest

@pytest.fixture
def mock_all_subtasks(monkeypatch):
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.check_path_is_available', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.copy_folder_from_path', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.download_template', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.apply_customizations', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.generate_readme', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.init_local_repo', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.push_first_commit', lambda *args, **kwargs: None)
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.install_project', lambda *args, **kwargs: None)
    # This one should never get called
    monkeypatch.setattr('be_bi_pyqt_project_manager.create_project.invoke_git', lambda *args, **kwargs: 1/0)
    yield






