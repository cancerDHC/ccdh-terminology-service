import csv
import json
import logging
from pathlib import Path
from typing import List

from ccdh import ROOT_DIR

logger = logging.getLogger('ccdh.importers.gdc')
logger.setLevel(logging.DEBUG)

GDC_JSON_FILE = ROOT_DIR / 'data/data_dictionary/gdc/current.json'
GDC_MAPING_DIR = ROOT_DIR / 'data/mappings/gdc-ncit'


class GdcImporter:
    def __init__(self):
        ...

    @staticmethod
    def read_data_dictionary() -> List:
        data_elements = {}
        logger.info(f'Loading {GDC_JSON_FILE}')
        dd = json.loads(GDC_JSON_FILE.read_text())
        for key, entity in dd.items():
            if key == '_definitions' or key == '_terms':
                continue
            entity_name = entity['title']
            for prop, values in entity['properties'].items():
                if 'enum' in values:
                    permissible_values = values['enum']
                    if 'deprecated_enum' in values:
                        permissible_values = list(set(permissible_values).difference(values['deprecated_enum']))
                    cde_id = values.get('termDev', {}).get('cde_id', None)
                    data_element = {
                        'context': 'GDC',
                        'entity': entity_name,
                        'attribute': prop,
                        'definition': values.get('description', None),
                        'permissible_values': permissible_values,
                        'cde': cde_id
                    }
                    data_elements[f'GDC.{entity_name}.{prop}'] = data_element
        return data_elements

    @staticmethod
    def read_ncit_mappings():
        gdc_ncit_map = {}
        gdc_ncit_file = GDC_MAPING_DIR / 'current.csv'
        with open(gdc_ncit_file, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            for row in reader:
                target_code = row[3]
                if target_code not in gdc_ncit_map:
                    gdc_ncit_map[target_code] = {}
                gdc_ncit_map[target_code][row[4]] = row
        return gdc_ncit_map

