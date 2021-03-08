# BI Python GUI Manager

This is the repository for the BI Python GUI Manager.

It is a tool for bootstrapping PyQt GUI projects, which:
- Provides a wizard to create and setup new Python-based BI Expert GUI projects based on a common template (
see [SY BI Pyqt Template](https://gitlab.cern.ch/bisw-python/sy-bi-pyqt-template))
- Configures existing projects (modify author name, email description, GitLab repo, etc...)
- Releases the project under the shared folder used by the BI Launcher for Python apps
  (`/user/bdisoft/development/python/gui/deployments`).
- Manages the project's entry points (commands available in the console to launch the PyQt application)
  and tries to ensure full compatibility with Acc-Py.

## Setup

A stable version of this script is available under `/user/bdisoft/development/python/gui/bipy-gui-manager`.

In order to use it, you should add it to your PATH or alias it - you can follow 1), 2) or 3) below:

#### 1) Add it to PATH under '~/.local/bin'
This method assumes that '~/.local/bin' is already in your PATH, or that you can add it yourself. It will
create a symlink to `bipy-gui-manager` under `~/.local/bin`

Simply type:
```bash
ln -s /user/bdisoft/development/python/gui/bipy-gui-manager ~/.local/bin/bipy-gui-manager
```

#### 2) Add it to PATH under '/usr/local/bin'
This method assumes that '/usr/local/bin' is already in your PATH, which is true for most users, and that you can
perform operations as `sudo`. It will create a symlink to `bipy-gui-manager` under `/usr/local/bin`

Simply type:
```bash
sudo ln -s /user/bdisoft/development/python/gui/bipy-gui-manager /usr/local/bin/bipy-gui-manager
```

#### 3) Alias it
This method will not modify your PATH and won't create symlinks, but requires you to edit your `~/.bashrc`.

Add the following line to your `~/.bashrc`:
```bash
alias bipy-gui-manager="/user/bdisoft/development/python/gui/bipy-gui-manager"
```
## Verify

Once you did one of the above, typing
```bash
bipy-gui-manager
```
should show you a help message.

## Usage

You can list all the functions available with
```bash
bipy-gui-manager --help
```

The most important are:
 - `bipy-gui-manager new`: starts a wizard that guides
you through the setup of a new PyQt project.
 - `bipy-gui-manager deploy <path>`: deploys the specified application 
   on a BI custom Acc-Py repository on NFS. Applications
   deployed in this way can be later added to the 
   [BI AppLauncher](https://gitlab.cern.ch/bisw-java-fwk/bi-launcher).
 - `bipy-gui-manager run <app_name>`: uses Acc-Py to launch any application
   that was deployed with the above command.

Each of these commands have their own options. For example, to know more about the
options available for `new`, type
```bash
bipy-gui-manager new --help
```


## Contribute
If you are a developer and want to contribute, or you're taking over this project:

#### Install
First, activate Acc-Py. Then:
```bash
sudo yum install -y openldap-devel python-devel   # Required for pyphonebook, one of the dependencies
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
