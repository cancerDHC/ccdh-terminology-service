"""Delete Neo4J database

This is a quick and dirty alternative to doing this programatically. Up until now,
I've been doing his by manually loading up the Neo4J browser, and running the query/command:
`match (n) detach delete n;
"""
import os
import shutil
from argparse import ArgumentParser
from datetime import datetime
from glob import glob


from typing import List

ROOT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
NEO4J_VOLUME_PATH_PRODUCTION = os.path.join(ROOT_DIR, 'docker', 'volumes', 'prod', 'neo4j')
NEO4J_VOLUME_PATH_TEST = os.path.join(ROOT_DIR, 'docker', 'volumes', 'test', 'neo4j')
BACKUP_FOLDER_NAME = '_archive'
BACKUP_FOLDERS_TO_IGNORE = [BACKUP_FOLDER_NAME]
DELETE_DIRNAME_CONTENT_MAP = {
    'conf': ['neo4j.conf'],
    'data': ['databases', 'dbms', 'transactions'],
    'logs': ['debug.log']
}


def run(env_name: str = 'production', backup: bool = True):
    """Run"""
    db_folder_path: str = {
        'production': NEO4J_VOLUME_PATH_PRODUCTION,
        'test': NEO4J_VOLUME_PATH_TEST
    }[env_name]
    to_copy: List[str] = glob(os.path.join(db_folder_path, '*'))

    if backup:
        this_backup_folder_name = str(datetime.now())[:-7].replace(':', '_')
        this_backup_folder_path = os.path.join(db_folder_path, BACKUP_FOLDER_NAME, this_backup_folder_name)
        os.makedirs(this_backup_folder_path)

        to_copy = [x for x in to_copy
                   if not any([x.endswith(y) for y in BACKUP_FOLDERS_TO_IGNORE])]
        for x in to_copy:
            destination = os.path.join(this_backup_folder_path, os.path.basename(x))
            if os.path.isfile(x):
                shutil.copy(x, destination)
            elif os.path.isdir(x):
                shutil.copytree(x, destination)

    to_delete: List[str] = []
    for foldername, contents in DELETE_DIRNAME_CONTENT_MAP.items():
        folder_path = os.path.join(db_folder_path, foldername)
        for folder_or_file in contents:
            to_delete.append(os.path.join(folder_path, folder_or_file))

    for x in to_delete:
        if os.path.isfile(x):
            os.remove(x)
        elif os.path.isdir(x):
            shutil.rmtree(x)
    print()


def get_parser():
    """Add required fields to parser.

    Returns:
        ArgumentParser: Argeparse object.
    """
    package_description = 'Delete Neo4j database through file system deletions.'
    parser = ArgumentParser(description=package_description)

    parser.add_argument(
        '-e', '--env-name', default='production',
        choices=['production', 'test'],
        help='Env name: "test" or "production"')

    parser.add_argument(
        '-b', '--backup', action='store_true', help='Save a backup?')

    return parser


def cli():
    """Command line interface for package.

    Side Effects: Executes program.

    Command Syntax:

    Examples:

    """
    parser = get_parser()
    kwargs = parser.parse_args()

    run(env_name=kwargs.env_name,
        backup=kwargs.backup)


if __name__ == '__main__':
    cli()
