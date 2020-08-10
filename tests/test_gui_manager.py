from bipy_gui_manager.main import main


def test_main(monkeypatch):
    # Stub test for the main switch
    monkeypatch.setattr('sys.argv', ["bipy_gui_manager", "create-project"])
    monkeypatch.setattr('bipy_gui_manager.create_project.create_project.create_project',
                        lambda *a, **k: None)
    main()
