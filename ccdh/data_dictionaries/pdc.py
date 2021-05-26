import sys
from collections import namedtuple

import glob
import logging
import yaml
from pathlib import Path
import csv
from ccdh.data_dictionaries.gdc import expand_rows
from ccdh.data_dictionaries.cdm import cdm_dictionary_sheet

GDC_DIR = Path(__file__).parent.parent / 'crdc-nodes/gdcdictionary'
sys.path.append(str(GDC_DIR))

from gdcdictionary.python import visit_directory


PDC_ROOT = Path(__file__).parent.parent / 'PDC-public/documentation/prod/yaml'

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


def pdc_values(rows):
    pdc = PDCDictionary(root_dir=PDC_ROOT)
    new_rows = []
    for row in rows:
        node, entity, attr = row[0].split('.')
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
        else:
            cde_id = props[attr].get('cde_id', '')
            codes = props[attr].get('enum', [])
            new_rows.extend(expand_rows(row, codes, cde_id))
    return new_rows


def main():
    rows = pdc_values(cdm_dictionary_sheet('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4'))
    with open('pdc.tsv', 'w', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        for row in rows:
            tsv_output.writerow(row)


if __name__ == '__main__':
    main()