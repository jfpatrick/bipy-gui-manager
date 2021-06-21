#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import os
import sys
import signal
import argparse
import argcomplete

from bipy_gui_manager.utils import cli as cli
from bipy_gui_manager.new.new_project import new_project
from bipy_gui_manager.deploy.deploy import deploy
from bipy_gui_manager.run.run import run, get_runnable_apps_for_argcomplete


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
    parser = argparse.ArgumentParser(epilog=f"type '{os.path.basename(sys.argv[0])} "
                                            f"<command> --help' to learn more about their options.")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help="Set the logger to verbose mode (useful to report bugs).")

    subparsers = parser.add_subparsers()

    # 'new' subcommand
    new_project_parser = subparsers.add_parser('new',
                                               help='Start a wizard that guides you through the setup of a new PyQt '
                                                    'project.')
    new_project_parser.set_defaults(func=new_project)
    new_project_parser.add_argument('--path', dest='base_path', default=None,
                                    help="Specify the path to the new project. "
                                         "If not set, uses the current working directory.")
    new_project_parser.add_argument('--name', dest='project_name', default=None,
                                    help="Sets the project name.")
    new_project_parser.add_argument('--desc', dest='project_desc', default=None,
                                    help="Sets the project's short description.")
    new_project_parser.add_argument('--author', dest='project_author', default=None,
                                    help="Sets the project author's CERN ID (must be valid).")
    new_project_parser.add_argument('--verbose', dest='verbose', action='store_true',
                                    help="Raises the logging level to the maximum")
    new_project_parser.add_argument('--type', dest='project_type', default=None,
                                    help="Chooses between the ComRAD and the PyQt project template."
                                    "Set it to 'comrad' to have a setup ready for ComRAD, "
                                    "or to 'pyqt' to download the app template and the proper libraries.")
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
    new_project_parser.add_argument('--template-url', dest='template_url',
                                    help="[DEBUG] Copy the template from a custom URL."
                                         "NOTE: further customizations might break if the template does not correspond "
                                         "to the default one.")
    new_project_parser.add_argument('--crash', dest='crash', action='store_true',
                                    help="[DEBUG] Do not try to recover from errors.")

    # Separate parser for duplicate flags
    # (https://stackoverflow.com/questions/7498595/python-argparse-add-argument-to-multiple-subparsers)
    op_dev_parser = argparse.ArgumentParser(add_help=False)
    op_dev = op_dev_parser.add_mutually_exclusive_group(required=True)
    op_dev.add_argument('--operational', '-o', action="store_true",
                        help="Use the operational deployments path")
    op_dev.add_argument('--development', '-d', action="store_true",
                        help="Use the development deployments path")

    # 'deploy' subcommand
    deploy_parser = subparsers.add_parser('deploy', parents=[op_dev_parser],
                                          help="Deploys the application in a shared folder, so it can be started "
                                               "from BI's AppLauncher")
    deploy_parser.set_defaults(func=deploy)
    deploy_parser.add_argument('path', nargs='?', default=os.getcwd(),
                               help="Path to the folder to deploy. Defaults to the current directory.")
    deploy_parser.add_argument('--entry-point', dest='entry_point', default=None, type=str,
                               help="The entry point name. This parameter is required only if the entry point name "
                                    "differs from the project name.")

    # 'run' subcommand

    run_parser = subparsers.add_parser('run', parents=[op_dev_parser],
                                       help="Executes the application from a shared folder.")
    run_parser.set_defaults(func=run)
    run_parser.add_argument('app', nargs='?', metavar="APP_NAME",
                            choices=get_runnable_apps_for_argcomplete(),
                            help="Name of the deployed app to run.")

    # Parse and call relevant subcommand
    argcomplete.autocomplete(parser)
    argcomplete.autocomplete(op_dev_parser)
    arguments = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    arguments.func(arguments)  # Necessary for the subparsers
