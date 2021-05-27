import csv
import glob
import logging
import sys
from collections import namedtuple
from copy import deepcopy
from pathlib import Path

import yaml

GDC_DIR = Path(__file__).parent.parent.parent / 'crdc-nodes/gdcdictionary'
sys.path.append(str(GDC_DIR))

from gdcdictionary.python import visit_directory

ICDC_ROOT = Path(__file__).parent.parent.parent / 'crdc-nodes/icdc-model-tool/model-desc'

ResolverPair = namedtuple('ResolverPair', ['resolver', 'source'])


class ICDCDictionary(object):

    logger = logging.getLogger("ICDCDictionary")

    def __init__(self, lazy=False, root_dir=None):
        """Creates a new dictionary instance.
        :param root_dir: The directory to find schemas
        """

        self.root_dir = root_dir
        self.properties = dict()
        self.entities = dict()
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
            for path in glob.glob("*.yml"):
                schema = self.load_yaml(path)
                schemas[path] = schema

        return schemas

    def load_directory(self, directory):
        """Load and reslove all schemas from directory"""

        yamls = self.load_schemas_from_dir(directory)
        self.properties = yamls['icdc-model-props.yml']['PropDefinitions']
        self.entities = yamls['icdc-model.yml']['Nodes']


def icdc_values(rows):
    icdc = ICDCDictionary(root_dir=ICDC_ROOT)
    new_rows = []
    for row in rows:
        node, entity, attr = row[-4:-1]
        value_found = True
        if node.upper() != 'ICDC':
            value_found = False
        elif entity.lower() not in icdc.entities:
            print(f'ICDC | {entity} not found')
            value_found = False
        else:
            if attr.lower() not in icdc.properties:
                print(f'PDC | {entity} | {attr} not found')
                value_found = False
        if not value_found:
            new_rows.append(row)
            continue
        for code in icdc.properties[attr.lower()].get('Type', []):
            new_row = deepcopy(row)
            new_row[-1] = code
            new_rows.append(new_row)
    return new_rows
