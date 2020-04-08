import sys
import argparse

from be_bi_pyqt_project_manager.create_project import create_project


def main():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help='Possible operations:')
    new_project_parser = subparsers.add_parser('create-project',
           help='Start a wizard that guides you through the setup of a new PyQt project.')
    new_project_parser.set_defaults(func=create_project)

    entry_points_parser = subparsers.add_parser('entry-points',
           help='Manages the application\'s entry points.')

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    args.func(args)

if __name__ == '__main__':
    main()
