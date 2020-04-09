import sys
import argparse

from be_bi_pyqt_project_manager.create_project import create_project
from be_bi_pyqt_project_manager.self_update import self_update
from be_bi_pyqt_project_manager.configure import configure
from be_bi_pyqt_project_manager.entry_points import entry_points


def main():
    parser = argparse.ArgumentParser(epilog="type 'pyqt-manager <command> --help' to learn more about their options.")
    subparsers = parser.add_subparsers()

    new_project_parser = subparsers.add_parser('create-project',
           help='Start a wizard that guides you through the setup of a new PyQt project.')
    new_project_parser.set_defaults(func=create_project)
    new_project_parser.add_argument('--no-demo', dest='demo', action='store_false',
            help="Install the template without demo application")

    self_update_parser = subparsers.add_parser('self-update',
           help='Checks for updates for pyqt-manager (does not affects applications).')
    self_update_parser.set_defaults(func=self_update)

    project_configuration_parser = subparsers.add_parser('configure',
            help='Checks for updates for pyqt-manager (does not affects applications).')
    project_configuration_parser.set_defaults(func=configure)

    entry_points_parser = subparsers.add_parser('entry-points',
            help='Manages the application\'s entry points.')
    entry_points_parser.set_defaults(func=entry_points)

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    args.func(args)  # Necessary for the subparsers


if __name__ == '__main__':
    main()
