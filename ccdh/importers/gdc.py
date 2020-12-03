import json
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger('ccdh.importers.GdcImporter')
logger.setLevel(logging.DEBUG)

GDC_JSON_FILE = Path(__file__).parent.parent.parent / 'data/data_dictionary/gdc/current.json'


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
                    cde_id = values.get('termDev', {}).get('cde_id', None)
                    data_element = {
                        'context': 'GDC',
                        'entity': entity_name,
                        'attribute': prop,
                        'definition': values.get('description', None),
                        'permissible_values': values['enum'],
                        'cde': cde_id
                    }
                    data_elements[f'GDC.{entity_name}.{prop}'] = data_element
        return data_elements

