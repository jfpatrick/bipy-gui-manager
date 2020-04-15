# BE-BI PyQt Project Manager

This is the repository for the BE-BI PyQt Project Manager.

It is a tool for bootstrapping PyQt GUI projects, which:
- Provides a wizard to create and setup new projects with a predefined project structure (
see [BE BI Pyqt Template](https://gitlab.cern.ch/szanzott/be-bi-pyqt-template))
- Configures existing projects (modify author name, email description, GitLab repo, etc...)
- Releases the project on the CERN Python repository
- Manages the project's entry points (commands available in the console to launch the PyQt application)
- Self-updates

## Getting started

#### Install

Assuming Python 3.6 is installed, or `acc-pyqt` is active in your shell
([more info here](https://wikis.cern.ch/display/ACCPY/PyQt+distribution)), type:
```bash
pip install --user be-bi-pyqt-project-manager
```

If `pip` is not present in your system, try instead:
```bash
python3 -m pip install --user be-bi-pyqt-project-manager
```

To make sure the installation was successful, type:
```bash
pyqt-manager
```
You should see a help message.

## Usage

You can list all the functions available with
```bash
pyqt-manager --help
```

The most important are:
 - `pyqt-manager create-project`: starts a wizard that guides
you through the setup of a new PyQt project.
 - `pyqt-manager release`: release the project on CERN's repos _TODO_ .
 - `pyqt-manager dev-release`: _TODO when CO will have a strategy for this_.
 - `pyqt-manager self-update`: checks whether any update for itself _TODO_
is available and, if so, update itself. Does not affect the application's code.
 - `pyqt-manager update-project`: checks whether any update for the
project's dependencies is available and, if so, install them _TODO_.
 - `pyqt-manager entry-points`: manages the entry-points of your application,
if any. _TODO_


## Contribute
If you are a developer and want to contribute, or you're taking over this project:

#### Setup
Do the following every time you begin working:
```
cd be-bi-pyqt-project-manager/
git pull
```

Also, please keep this README up-to-date and useful :)
