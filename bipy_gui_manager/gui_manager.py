import sys
import argparse

from bipy_gui_manager.create_project import create_project
from bipy_gui_manager.self_update import self_update
from bipy_gui_manager.configure import configure
from bipy_gui_manager.entry_points import entry_points


def main():
    parser = argparse.ArgumentParser(epilog="type 'pyqt-manager <command> --help' to learn more about their options.")
    subparsers = parser.add_subparsers()

    new_project_parser = subparsers.add_parser('create-project',
                                               help='Start a wizard that guides you through the setup of a new PyQt '
                                                    'project.')
    new_project_parser.set_defaults(func=create_project)
    new_project_parser.add_argument('--path', dest='project_path', default="",
                                    help="Specify the path to the new project. "
                                         "If not set, uses the current working directory.")
    new_project_parser.add_argument('--name', dest='project_name', default="",
                                    help="Sets the project name.")
    new_project_parser.add_argument('--desc', dest='project_desc', default="",
                                    help="Sets the project's short description.")
    new_project_parser.add_argument('--author', dest='project_author', default="",
                                    help="Sets the project author's name.")
    new_project_parser.add_argument('--email', dest='author_email', default="",
                                    help="Sets the project author's email.")
    new_project_parser.add_argument('--repo', dest='gitlab_repo', default="",
                                    help="Sets the project's GitLab repository address'.")
    new_project_parser.add_argument('--no-gitlab', dest='gitlab', action='store_false',
                                    help="Skips the GitLab upload, but still inits the repository locally.")
    new_project_parser.add_argument('--clone-protocol', dest='clone_protocol', default="kerberos",
                                    choices=('kerberos', 'ssh', 'https'),
                                    help="Protocol to use to clone the template from GitLab")
    demo_commands = new_project_parser.add_mutually_exclusive_group()
    demo_commands.add_argument('--no-demo', dest='demo', action='store_false',
                               help="Install the template without demo application without asking the user "
                                    "(the default behavior is to ask the user interactively, "
                                    "or to install the demo in case --not-interactive is passed)")
    demo_commands.add_argument('--with-demo', dest='force_demo', action='store_true',
                               help="Install the template with the demo application without asking the user "
                                    "(the default behavior is to ask the user interactively, "
                                    "or to install the demo in case --not-interactive is passed)")
    new_project_parser.add_argument('--not-interactive', dest='interactive', action='store_false',
                                    help="Prevents the script from asking the user, interactively, for missing "
                                         "information. If any of the flags --name, --desc, --author, --email is "
                                         "not specified, the script will fail.")
    new_project_parser.add_argument('--overwrite-project', dest='overwrite', action='store_true',
                                    help="[DEBUG] Overwrites a potentially existing project with the same name without "
                                         "asking the user. This prevents --not-interactive from failing if the "
                                         "project exists, but MIGHT CAUSE DATA LOSS!")
    new_project_parser.add_argument('--template-path', dest='template_path',
                                    help="[DEBUG] Copy the template from a custom location on the filesystem. "
                                         "NOTE: further customizations might break if the template does not correspond "
                                         "to the default one.")

    self_update_parser = subparsers.add_parser('self-update',
           help='Checks for updates for pyqt-manager (does not affects applications).')
    self_update_parser.set_defaults(func=self_update)

    project_configuration_parser = subparsers.add_parser('configure',
            help='Configure the current project (set author, email, etc...).')
    project_configuration_parser.set_defaults(func=configure)

    entry_points_parser = subparsers.add_parser('entry-points',
            help='Manages the application\'s entry points.')
    entry_points_parser.set_defaults(func=entry_points)

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    args.func(args)  # Necessary for the subparsers
