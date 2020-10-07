from copy import deepcopy
from collections import namedtuple
from contextlib import contextmanager
from jsonschema import RefResolver

import glob
import logging
import os
import yaml
from pathlib import Path
from ccdh.cdm import cdm_dictionary_sheet
from copy import deepcopy
import csv


MOD_DIR = Path(__file__).parent.parent.joinpath('gdcdictionary/gdcdictionary')
MAP_DIR = Path(__file__).parent.parent.joinpath('mappings/gdc-ncit')

ResolverPair = namedtuple('ResolverPair', ['resolver', 'source'])

@contextmanager
def visit_directory(path):
    """Perform contained actions with current working directory at
    :param:``path``.  Always return to previous directory when done.
    """

    cdir = os.getcwd()
    try:
        os.chdir(path)
        yield os.getcwd()
    finally:
        os.chdir(cdir)


def gdc_ncit_mappings():
    target_code_map = {}
    target_code_file = MAP_DIR / 'NCIt_AB_vs_GDC_Property_10_02_2020.csv'
    with open(target_code_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            target_code_map[row[0]] = row[1]
    gdc_ncit_map = {}
    gdc_ncit_file = MAP_DIR / 'NCIt_Maps_To_GDC.csv'
    with open(gdc_ncit_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            # Note, there was one typo in one Target_Code, it has been fixed it in Protege but the data CCDH has
            # (likely the 20.08e file) will have MOPRH as an abbreviation, which should have been MORPH.
            if row[3] == 'MOPRH':
                row[3] = 'MORPH'
            target_code = target_code_map[row[3]]
            if target_code not in gdc_ncit_map:
                gdc_ncit_map[target_code] = {}
            gdc_ncit_map[target_code][row[4]] = row
    return gdc_ncit_map


class GDCDictionary(object):

    _metaschema_path = 'metaschema.yaml'
    _definitions_paths = [
        '_definitions.yaml',
        '_terms.yaml',
    ]

    logger = logging.getLogger("GDCDictionary")

    def __init__(self, lazy=False, root_dir=None, definitions_paths=None,
                 metaschema_path=None):
        """Creates a new dictionary instance.
        :param root_dir: The directory to find schemas
        :param metaschema_path: The metaschema to validate schemas with
        :param definitions_paths: Paths to resolve $ref to
        :param lazy: If true, wait to load dictionary
        """

        self.metaschema = None

        self.root_dir = (root_dir or os.path.join(MOD_DIR, 'schemas'))
        self.metaschema_path = metaschema_path or self._metaschema_path
        self.definitions_paths = definitions_paths or self._definitions_paths
        self.exclude = [self.metaschema_path] + self.definitions_paths
        self.schema = dict()
        self.resolvers = dict()
        if not lazy:
            self.load_directory(self.root_dir)

    def load_yaml(self, name):
        """Return contents of yaml file as dict"""
        # For DAT-1064 Bomb out hard if unicode is in a schema file
        # But allow unicode through the terms and definitions
        with open(name, 'r') as f:
            if name not in self.exclude:
                try:
                    f.read().encode("ascii")
                    f.seek(0)
                except Exception as e:
                    self.logger.error("Error in file: {}".format(name))
                    raise e
            return yaml.safe_load(f)

    def load_schemas_from_dir(self, directory):
        """Returns all yamls and resolvers of those yamls from dir"""

        schemas, resolvers = {}, {}

        with visit_directory(directory):
            for path in glob.glob("*.yaml"):
                schema = self.load_yaml(path)
                schemas[path] = schema
                resolver = RefResolver('{}#'.format(path), schema)
                resolvers[path] = ResolverPair(resolver, schema)

        return schemas, resolvers

    def load_directory(self, directory):
        """Load and reslove all schemas from directory"""

        yamls, resolvers = self.load_schemas_from_dir(directory)

        self.metaschema = yamls[self.metaschema_path]
        self.resolvers.update(resolvers)

        schemas = {
            schema['id']: self.resolve_schema(schema, deepcopy(schema))
            for path, schema in yamls.items()
            if path not in self.exclude
        }
        self.schema.update(schemas)

    def resolve_reference(self, value, root):
        """Resolves a reference.
        :param value: The actual reference, e.g. ``_yaml.yaml#/def``
        :param root:
            The containing root of :param:`value`. This needs to be
            passed in order to resolve self-referential $refs,
            e.g. ``#/def``.
        :returns: JSON Schema pointed to by :param:`value`
        """
        base, ref = value.split('#', 1)

        if base:
            resolver, new_root = self.resolvers[base]
            referrer, resolution = resolver.resolve(value)
            self.resolve_schema(resolution, new_root)
        else:
            resolver = RefResolver('#', root)
            referrer, resolution = resolver.resolve(value)

        return resolution

    def resolve_schema(self, obj, root):
        """Recursively resolves all references in a schema against
        ``self.resolvers``.
        :param obj: The object to recursively resolve.
        :param root:
            The containing root of :param:`value`. This needs to be
            passed in order to resolve self-referential $refs,
            e.g. ``#/def``.
        :returns: A denormalized/resolved version of :param:`obj`.
        """

        if isinstance(obj, dict):
            for key in obj.copy().keys():
                if key == '$ref':
                    refs = obj.pop(key)
                    self.resolve_local_refs(refs, obj, root)
            return {k: self.resolve_schema(v, root) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.resolve_schema(item, root) for item in obj]
        else:
            return obj

    def resolve_local_refs(self, refs, obj, root):
        """Converts a string ref to list of refs & resolves the references
        """
        if not isinstance(refs, list):
            refs = [refs]
        for ref in refs:
            obj.update(self.resolve_reference(ref, root))


def gdc_values(rows):
    gdc = GDCDictionary()
    gdc_ncit_map = gdc_ncit_mappings()
    new_rows = []
    for row in rows:
        node, entity, attr = row[2:5]
        yaml_file = f'{entity.lower()}.yaml'
        value_found = True
        if node.upper() != 'GDC':
            value_found = False
        elif yaml_file not in gdc.resolvers:
            print(f'GDC | {yaml_file} not found')
            value_found = False
        else:
            props = gdc.resolvers[yaml_file].source.get('properties', {})
            if attr not in props:
                print(f'GDC | {entity} | {attr} not found')
                value_found = False
        if not value_found:
            new_rows.append(row)
            continue
        cde_id = props[attr].get('termDef', {}).get('cde_id', '') or ''
        for code in props[attr].get('enum', []):
            new_row = deepcopy(row)
            new_row[5] = code
            new_row[6] = str(cde_id)
            map_row = gdc_ncit_map[new_row[4]].get(new_row[5], [])
            if map_row:
                new_row[7] = map_row[0]
                new_row[8] = map_row[1]

            new_rows.append(new_row)

    return new_rows


def main():
    rows = gdc_values(cdm_dictionary_sheet('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4'))
    with open('gdc.tsv', 'w', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        for row in rows:
            tsv_output.writerow(row)


if __name__ == '__main__':
    main()