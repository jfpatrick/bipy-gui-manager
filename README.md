# BE-BI PyQt Project Manager

This is the repository for the BE-BI PyQt Project Manager.

It is a tool for bootstrapping PyQt GUI projects. It provides:
- A command-line wizard to help you get started & perform basic
maintenance operations
- A sane folder structure for your code, based on the MVP architecture.
- A test setup ready for unit tests and GUI tests (based on `pytest-qt`)
- A minimal simulation environment for your tests (based on 
[`papc`](https://gitlab.cern.ch/pelson/papc)), 
that can be extended to mimick your real data sources (FESA, NXCALS, ...)
- A `setup.py` to customize for quick packaging & release, with `entry_points`
- `.gitignore` with common Python artifacts
- `.gitlab-ci.yml` supporting GUI testing out of the box and coverage reports
- A small `activate.sh` activation script to activate both your virtualenv and Acc-Py, and
sets up some env vars for QtDesigner

For a detailed explanation of the project structure, head over to
[BE BI Pyqt Template](https://gitlab.cern.ch/szanzott/be-bi-pyqt-template).

## Getting started

#### Install
Assuming Python 3.6 is installed and `acc-pyqt` is active in your shell
([more info here](https://wikis.cern.ch/display/ACCPY/PyQt+distribution)), type:
```bash
pip install --user be-bi-pyqt-project-manager
```

If pip is not present in your system, try instead:
```bash
python3 -m pip install --user be-bi-pyqt-project-manager
```

To make sure the installation was successful, type:
```bash
pyqt-manager
```

## Usage

You can list all the functions available with
```bash
pyqt-manager --help
```

The most important are:
 - `pyqt-manager create-project`: starts a wizard that guides
you through the setup of a new PyQt project.
 - `pyqt-manager release`: release the project on CERN's repos.
 - `pyqt-manager dev-release`: _TODO_.
 - `pyqt-manager self-update`: checks whether any update for itself
is available and, if so, update itself. Does not affect the application's code.
 - `pyqt-manager update-project`: checks whether any update for the
project's dependencies is available and, if so, install them.
 - `pyqt-manager entry-points list`: lists all the entry-points of your application,
if any.
 - `pyqt-manager entry-points add`: adds an entry-points to your application.
 - `pyqt-manager entry-points delete`: adds an entry-points to your application.


## Contribute
If you are a developer and want to contribute, or you're taking over this project:

#### Setup
Do the following every time you begin working:
```
cd be-bi-pyqt-project-manager/
git pull
```

Also, please keep this README up-to-date and useful :)
