import sys
import signal
import argparse

from bipy_gui_manager import cli_utils as cli
from bipy_gui_manager.create_project.create_project import create_project


# Gracefully handle Ctrl+C and other kill signals
def kill_handler(_, __):
    cli.draw_line()
    cli.negative_feedback("Exiting on user's request.\n")
    sys.exit(0)


# Hook the custom handler to the kill signal
signal.signal(signal.SIGINT, kill_handler)


def main():
    """
    This function acts mainly as a frontend for the different subcommands.
    """
    parser = argparse.ArgumentParser(epilog="type 'pyqt-manager <command> --help' to learn more about their options.")
    subparsers = parser.add_subparsers()

    # 'create-project' subcommand
    new_project_parser = subparsers.add_parser('create-project',
                                               help='Start a wizard that guides you through the setup of a new PyQt '
                                                    'project.')
    new_project_parser.set_defaults(func=create_project)
    new_project_parser.add_argument('--path', dest='base_path', default=None,
                                    help="Specify the path to the new project. "
                                         "If not set, uses the current working directory.")
    new_project_parser.add_argument('--name', dest='project_name', default=None,
                                    help="Sets the project name.")
    new_project_parser.add_argument('--desc', dest='project_desc', default=None,
                                    help="Sets the project's short description.")
    new_project_parser.add_argument('--author', dest='project_author', default=None,
                                    help="Sets the project author's CERN ID (must be valid).")
    repo_commands = new_project_parser.add_mutually_exclusive_group()
    repo_commands.add_argument('--repo', dest='gitlab_repo', default=None,
                               help="Sets the project's GitLab repository address."
                                    "Set it to 'operational' to have a repo created under 'bisw-python' "
                                    "or to 'test' to have a repo created in your personal space.")
    repo_commands.add_argument('--no-gitlab', dest='gitlab', action='store_false',
                               help="Skips the GitLab upload, but still inits the repository locally.")
    new_project_parser.add_argument('--clone-protocol', dest='clone_protocol', default="kerberos",
                                    choices=('kerberos', 'ssh', 'https'),
                                    help="Protocol to use to clone the template from GitLab")
    new_project_parser.add_argument('--upload-protocol', dest='upload_protocol', default=None,
                                    choices=('kerberos', 'ssh', 'https'),
                                    help="Protocol to use to push the template to GitLab. "
                                         "Effective only if the --repo flag is set to 'default'. "
                                         "If not given, this value defaults to --clone-protocol")
    new_project_parser.add_argument('--gitlab-auth-token', dest='gitlab_token', default=None,
                                    help="GitLab private access token. Can be used to avoid the password prompt.")
    demo_commands = new_project_parser.add_mutually_exclusive_group()
    demo_commands.add_argument('--no-demo', dest='demo', action='store_false', default=None,
                               help="Install the template without demo application without asking the user "
                                    "(the default behavior is to ask the user interactively, "
                                    "or to install the demo in case --not-interactive is passed)")
    demo_commands.add_argument('--with-demo', dest='demo', action='store_true', default=None,
                               help="Install the template with the demo application without asking the user "
                                    "(the default behavior is to ask the user interactively, "
                                    "or to install the demo in case --not-interactive is passed)")
    new_project_parser.add_argument('--not-interactive', dest='interactive', action='store_false',
                                    help="Prevents the script from asking the user, interactively, for missing "
                                         "information. If any necessary information is not specified through the CLI, "
                                         "the script will fail.")
    new_project_parser.add_argument('--cleanup-on-failure', dest='cleanup_on_failure', action='store_true',
                                    help="In case of failure, delete any file created until then without asking.")
    new_project_parser.add_argument('--overwrite-project', dest='overwrite', action='store_true',
                                    help="[DEBUG] Overwrites a potentially existing project with the same name without "
                                         "asking the user. This prevents --not-interactive from failing if the "
                                         "project exists, but MIGHT CAUSE DATA LOSS!")
    new_project_parser.add_argument('--template-path', dest='template_path',
                                    help="[DEBUG] Copy the template from a custom location on the filesystem. "
                                         "NOTE: further customizations might break if the template does not correspond "
                                         "to the default one.")
    new_project_parser.add_argument('--crash', dest='crash', action='store_true',
                                    help="[DEBUG] Do not try to recover from errors.")
    new_project_parser.add_argument('--verbose', dest='verbose', action='store_true',
                                    help="Set the logger to verbose mode (useful to report bugs).")

    # 'release' subcommand
    # release_parser = subparsers.add_parser('release',
    #        help="Releases the application in the shared folders, to it becomes visible from BI's AppLauncher")
    # release_parser.set_defaults(func=release)

    # 'configure' subcommand
    # project_configuration_parser = subparsers.add_parser('configure',
    #         help='Configure the current project (set author, email, etc...).')
    # project_configuration_parser.set_defaults(func=configure)
    #
    # # 'entry-points' subcommand
    # entry_points_parser = subparsers.add_parser('entry-points',
    #         help='Manages the application\'s entry points.')
    # entry_points_parser.set_defaults(func=entry_points)

    # Parse and call relevant subcommand
    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    args.func(args)  # Necessary for the subparsers
