# BI Python GUI Manager

This is the repository for the BI Python GUI Manager.

It is a tool for bootstrapping PyQt GUI projects, which:
- Provides a wizard to create and setup new projects based on a common template (
see [BE BI Pyqt Template](https://gitlab.cern.ch/bisw-python/be-bi-pyqt-template))
- Configures existing projects (modify author name, email description, GitLab repo, etc...)
- Releases the project under the shared folder `/user/bdisoft/<development or operational>/python/gui` and versions it.
- Manages the project's entry points (commands available in the console to launch the PyQt application)

## Getting started

A stable version of this script is available under `/user/bdisoft/development/python/gui/bipy-gui-manager`.

In order to use it, execute:
```bash
source /user/bdisoft/development/python/gui/bipy-gui-manager/enable.sh
```
in your terminal. Once done, you can type
```bash
bipy-gui-manager
```
and a help message should appear.

## Usage

You can list all the functions available with
```bash
bipy-gui-manager --help
```

The most important are:
 - `bipy-gui-manager create-project`: starts a wizard that guides
you through the setup of a new PyQt project.
 - _TODO_ `bipy-gui-manager release`: releases the project under the `operational` folder of `/user/bdisoft/`.
 - _TODO_ `bipy-gui-manager dev-release`: releases the project under the `development` folder of `/user/bdisoft/`.
 - _TODO_ `bipy-gui-manager update-project`: checks whether any update for the
project's dependencies is available and, if so, install them.
 -  _TODO_ `bipy-gui-manager entry-points`: manages the entry-points of your application, if any.

Each of these commands have their own options. For example, to know more about the
options available for `create-project`, type
```bash
bipy-gui-manager create-project --help
```


## Contribute
If you are a developer and want to contribute, or you're taking over this project:

#### Install
First, activate Acc-Py. Then:
```bash
git clone https://:@gitlab.cern.ch:8443/bisw-python/bipy-gui-manager.git
cd bipy-gui-manager
acc-py venv venv
source venv/bin/activate
pip install -e .[all]
```

#### Setup
Do the following every time you begin working:
```
cd bipy-gui-manager/
git pull
```

Also, please keep this README up-to-date and useful :)
