import csv
import json
import logging
import os
from typing import List, Union
import requests
from requests.exceptions import HTTPError
from datetime import datetime

from ccdh import ROOT_DIR
from ccdh.importers.cadsr import get_cadsr_values

logger = logging.getLogger('ccdh.importers.gdc')
logger.setLevel(logging.DEBUG)

GDC_JSON_FILE = ROOT_DIR / 'data/data_dictionary/gdc/current.json'
GDC_MAPING_DIR = ROOT_DIR / 'data/mappings/gdc-ncit'


class GdcImporter:
    def __init__(self):
        ...

    @staticmethod
    def get_value_descriptions_from_cadsr(cde_id: Union[str, None]):
        if cde_id is None:
            return {}
        values = get_cadsr_values(cde_id)
        value_desc = {}
        if values is None:
            logger.warning("CDE ID contains no values: " + cde_id)
            return {}
        for v in values:
            value_desc[v.code] = v.display
        return value_desc

    @staticmethod
    def read_data_dictionary() -> List:
        harmonized_attributes = {}
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
                    cde_id = values.get('termDef', {}).get('cde_id', None)
                    harmonized_attribute = {
                        'system': 'GDC',
                        'entity': entity_name,
                        'attribute': prop,
                        'definition': values.get('description', None),
                        # 'permissible_values': permissible_values,
                        # 'cadsr_cde': cde_id
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
                        harmonized_attribute['cadsr_cde'] = str(cde_id)
                    harmonized_attribute['permissible_values'] = pvs
                    harmonized_attributes[f'GDC.{entity_name}.{prop}'] = harmonized_attribute
        return harmonized_attributes

    @staticmethod
    def update_data_dictionary():
        url = 'https://api.gdc.cancer.gov/v0/submission/_dictionary/_all'
        try:
            response = requests.get(url)
            # If the response was successful, no Exception will be raised
            data_dictionary = response.text
            datestr = datetime.today().strftime('%Y-%m-%d')
            jsonfile = ROOT_DIR / f'data/data_dictionary/gdc/gdc_data_dictionary-{datestr}.json'
            with open(jsonfile, 'w') as fout:
                fout.write(data_dictionary)
            if GDC_JSON_FILE.exists():
                os.unlink(GDC_JSON_FILE)
            os.symlink(jsonfile, GDC_JSON_FILE)
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
        else:
            print(f'GDC data dictionary saved to \n{jsonfile}\nand linked to \n{GDC_JSON_FILE}')

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


if __name__ == '__main__':
    GdcImporter.update_data_dictionary()
