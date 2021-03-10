===============================
SY/BI Python Expert GUI Manager
===============================

This is the documentation page for the SY/BI Expert GUI Manager.
It is a tool for bootstrapping PyQt GUI projects which:

* Provides a wizard to create and setup new Python-based BI Expert
  GUI projects based on a common template
  (see `SY BI Pyqt Template <https://gitlab.cern.ch/bisw-python/sy-bi-pyqt-template>`_).
* Configures existing projects (modify author name, email description, GitLab repo, etc...)
* Releases the project under the shared folder used by the BI Launcher for Python apps
  (``/user/bdisoft/operational/python/gui/deployments`` or
  ``/user/bdisoft/development/python/gui/deployments``)
* Manages the project's entry points (commands available in the console to launch the PyQt application)
  and tries to ensure full compatibility with Acc-Py.


Setup
=====
A stable version of this script is available under
``/user/bdisoft/operational/python/gui/bipy-gui-manager``.

Get the executable
------------------
In order to use it, you should add it to your ``PATH`` or alias it.
Choose one of the following options:

* **Add it to PATH under ~/.local/bin**:  this method assumes that ``~/.local/bin`` is already in your ``PATH``,
  or that you can add it yourself. It will create a symlink to
  ``bipy-gui-manager`` under ``~/.local/bin``. Simply type::

        ln -s /user/bdisoft/operational/python/gui/bipy-gui-manager ~/.local/bin/bipy-gui-manager

* **Add it to PATH under /usr/local/bin**:  This method assumes that ``/usr/local/bin`` is already in your
  ``PATH``, which is true for most users, and that you can perform operations as sudo. It will create a symlink
  to ``bipy-gui-manager`` under ``/usr/local/bin``. Simply type::

        sudo ln -s /user/bdisoft/operational/python/gui/bipy-gui-manager /usr/local/bin/bipy-gui-manager

* **Alias it**: This method will not modify your ``PATH`` and won't create symlinks, but requires you to edit your
  ``~/.bashrc``. Add the following line to your ``~/.bashrc``::

        alias bipy-gui-manager="/user/bdisoft/operational/python/gui/bipy-gui-manager"

Setup Autocompletion
--------------------
To have autocompletion for ``bipy-gui-manager``, register the executable by executing the following line
in your console::

    eval "$(register-python-argcomplete bipy-gui-manager)"


Verify
------
Once you did one of the above, typing::

    bipy-gui-manager

should show you a help message.

Usage
=====
You can list all the functions available with::

    bipy-gui-manager --help


The most important are:

* ``bipy-gui-manager new``: starts a wizard that guides you through the setup of a new PyQt project.
* ``bipy-gui-manager deploy <path>``: deploys the specified application on a BI custom Acc-Py repository
  on NFS. Applications deployed in this way can be later added to the
  `BI AppLauncher <https://gitlab.cern.ch/bisw-java-fwk/bi-launcher>`_.
* ``bipy-gui-manager run <app_name>``: uses Acc-Py to launch any application that was deployed with the above command.

Each of these commands have their own options. For example, to know more about the options available for
``new``, type::

    bipy-gui-manager new --help


To learn more about how to use it to create new projects, check out the
`SY/BI PyQt Tutorial <https://acc-py.web.cern.ch/gitlab/bisw-python/pyqt-tutorial/docs/stable/index.html>`_.

Contribute
==========
If you are a developer and want to contribute, or you're taking over this project, checkout the README
for this tool `on GitLab <https://gitlab.cern.ch/bisw-python/bipy-gui-manager>`_.


.. toctree::
    :maxdepth: 1
    :hidden:

    index
    genindex

