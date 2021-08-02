"""PDC (Proteomics Data Commons) Importer"""
import logging
import json
from typing import Dict

from ccdh import ROOT_DIR
from ccdh.importers.gdc import GdcImporter

logger = logging.getLogger('ccdh.importers.pdc')
logger.setLevel(logging.DEBUG)

PDC_JSON_DIR = ROOT_DIR / 'crdc-nodes/PDC-Public/documentation/prod/json'


class PdcImporter:
    """PDC Importer class"""
    def __init__(self):
        self.data_elements = []

    @staticmethod
    def read_data_dictionary() -> Dict:
        """Read data dictionary"""
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
                    cde_id = values.get('cde_id', None)
                    node_attribute = {
                        'system': 'PDC',
                        'entity': entity_name,
                        'attribute': prop,
                        'definition': values['description']
                    }
                    permissible_values = values['enum']
                    if 'deprecated_enum' in values:
                        permissible_values = list(set(permissible_values).difference(values['deprecated_enum']))
                    pvs = {}
                    for pv in permissible_values:
                        pvs[pv] = None
                    if cde_id is not None:
                        value_desc = GdcImporter.get_value_descriptions_from_cadsr(str(cde_id))
                        for pv in permissible_values:
                            if pv in value_desc:
                                pvs[pv] = value_desc[pv]
                        node_attribute['cadsr_cde'] = str(cde_id)
                    node_attribute['permissible_values'] = pvs
                    node_attributes[f'PDC.{entity_name}.{prop}'] = node_attribute
        return node_attributes
