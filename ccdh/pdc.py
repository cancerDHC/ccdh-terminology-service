from copy import deepcopy
from collections import namedtuple
from contextlib import contextmanager
from jsonschema import RefResolver

import glob
import logging
import os
import yaml
from pathlib import Path
from copy import deepcopy
import csv
from ccdh.gdc import visit_directory, gdc_values


PDC_ROOT = Path(__file__).parent.parent.joinpath('PDC-public/documentation/prod/yaml')

ResolverPair = namedtuple('ResolverPair', ['resolver', 'source'])


class PDCDictionary(object):

    logger = logging.getLogger("PDCDictionary")

    def __init__(self, lazy=False, root_dir=None):
        """Creates a new dictionary instance.
        :param root_dir: The directory to find schemas
        """

        self.root_dir = root_dir
        self.schema = dict()
        if not lazy:
            self.load_directory(self.root_dir)

    def load_yaml(self, name):
        """Return contents of yaml file as dict"""
        # For DAT-1064 Bomb out hard if unicode is in a schema file
        # But allow unicode through the terms and definitions
        with open(name, 'r') as f:
            try:
                f.read().encode("ascii")
                f.seek(0)
            except Exception as e:
                self.logger.error("Error in file: {}".format(name))
                raise e
            return yaml.safe_load(f)

    def load_schemas_from_dir(self, directory):
        """Returns all yamls and resolvers of those yamls from dir"""

        schemas = {}

        with visit_directory(directory):
            for path in glob.glob("*.yaml"):
                schema = self.load_yaml(path)
                schemas[path] = schema

        return schemas

    def load_directory(self, directory):
        """Load and reslove all schemas from directory"""

        yamls = self.load_schemas_from_dir(directory)
        schemas = {
            path: schema
            for path, schema in yamls.items()
            if self.include(path)
        }
        self.schema.update(schemas)

    def include(self, path):
        if 'Metadata' in path or 'dictionary' in path:
            return False
        return True

    def path_key(self, path):
        return path[:-5]


def pdc_values():
    pdc = PDCDictionary(root_dir=PDC_ROOT)
    rows = gdc_values()
    new_rows = []
    for row in rows:
        node, entity, attr = row[-4:-1]
        yaml_file = f'{entity.lower()}.yaml'
        value_found = True
        if node.upper() != 'PDC':
            value_found = False
        elif yaml_file not in pdc.schema:
            print(f'PDC | {yaml_file} not found')
            value_found = False
        else:
            props = pdc.schema[yaml_file].get('properties', {})
            if attr not in props:
                print(f'PDC | {entity} | {attr} not found')
                value_found = False
        if not value_found:
            new_rows.append(row)
            continue
        for code in props[attr].get('enum', []):
            new_row = deepcopy(row)
            new_row[-1] = code
            new_rows.append(new_row)
    return new_rows


def main():
    rows = pdc_values()
    with open('pdc.tsv', 'w', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        for row in rows:
            tsv_output.writerow(row)


if __name__ == '__main__':
    main()