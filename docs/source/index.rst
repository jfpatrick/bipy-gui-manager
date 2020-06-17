===============================
BE/BI Python Expert GUI Manager
===============================

This is the documentation page for the BE/BI Expert GUI Manager.
It is a tool for bootstrapping PyQt GUI projects, which:

* Provides a wizard to create and setup new Python-based BI Expert
  GUI projects based on a common template (see BE BI Pyqt Template).
* Releases the project under the shared folder
  ``/user/bdisoft/<development or operational>/python/gui``.

.. note:: This is technical and internal documentation for the tool itself.
    If you want to learn how to use it to create new projects, check out the
    `BE/BI PyQt Tutorial <https://acc-py.web.cern.ch/gitlab/bisw-python/pyqt-tutorial/docs/stable/index.html>`_.


Setup
=====
A stable version of this script is available under
``/user/bdisoft/development/python/gui/bipy-gui-manager``.
In order to use it, you should add it to your ``PATH`` or alias it.
Choose one of the following options:

# Add it to ``PATH`` under ``~/.local/bin``:  this method assumes that ``~/.local/bin`` is already in your ``PATH``,
  or that you can add it yourself. It will create a symlink to
  ``bipy-gui-manager`` under ``~/.local/bin``. Simply type::

        ln -s /user/bdisoft/development/python/gui/bipy-gui-manager ~/.local/bin/bipy-gui-manager

# Add it to ``PATH`` under ``/usr/local/bin``:  This method assumes that ``/usr/local/bin`` is already in your
  ``PATH``, which is true for most users, and that you can perform operations as sudo. It will create a symlink
  to ``bipy-gui-manager`` under ``/usr/local/bin``. Simply type::

        sudo ln -s /user/bdisoft/development/python/gui/bipy-gui-manager /usr/local/bin/bipy-gui-manager

# Alias it: This method will not modify your ``PATH`` and won't create symlinks, but requires you to edit your
  ``~/.bashrc``. Add the following line to your ``~/.bashrc``::

        alias bipy-gui-manager="/user/bdisoft/development/python/gui/bipy-gui-manager"

Verify
------
Once you did one of the above, typing::

    bipy-gui-manager

should show you a help message.

Usage
=====
To learn how to use it to create new projects, check out the
`BE/BI PyQt Tutorial <https://acc-py.web.cern.ch/gitlab/bisw-python/pyqt-tutorial/docs/stable/index.html>`_.

You can also list all the functions available with::

    bipy-gui-manager --help

Each of these commands have their own options. For example, to know more about the
options available for ``create-project``, type::

    bipy-gui-manager create-project --help

Contribute
==========
If you are a developer and want to contribute, or you're taking over this project, checkout the README
for this tool `on GitLab <https://gitlab.cern.ch/bisw-python/bipy-gui-manager>`_.


.. toctree::
    :maxdepth: 1
    :hidden:

    index
    api
    genindex

