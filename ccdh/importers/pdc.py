import logging
from pathlib import Path
import json
from typing import List

from ccdh import ROOT_DIR

logger = logging.getLogger('ccdh.importers.pdc')
logger.setLevel(logging.DEBUG)

PDC_JSON_DIR = ROOT_DIR / 'crdc-nodes/PDC-Public/documentation/prod/json'


class PdcImporter:
    def __init__(self):
        self.data_elements = []

    @staticmethod
    def read_data_dictionary() -> List:
        node_attributes = {}
        files = [f for f in PDC_JSON_DIR.glob('*.json') if f.is_file()]
        for file in files:
            if file.name == 'dictionary.json' or file.name == 'dictionary_item.json':
                continue
            logger.info(f'Loading {file.name}')
            entity = json.loads(file.read_text())
            entity_name = entity['title']
            for prop, values in entity['properties'].items():
                if 'type' not in values:
                    logger.info(file.name + ',' + prop)
                    continue
                if values.get('type', '') == 'Enumeration':
                    node_attribute = {
                        'system': 'PDC',
                        'entity': entity_name,
                        'attribute': prop,
                        'definition': values['description'],
                        'permissible_values': values['enum'],
                        'cadsr_cde': values.get('cde_id', None)
                    }
                    node_attributes[f'PDC.{entity_name}.{prop}'] = node_attribute
        return node_attributes





