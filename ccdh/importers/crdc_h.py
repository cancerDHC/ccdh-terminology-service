import logging
from typing import Dict
import requests
from googleapiclient.discovery import build
from linkml.loaders import yaml_loader
from linkml.utils.yamlutils import YAMLRoot

from ccdh.gdrive.authorize import authorize

logger = logging.getLogger('ccdh.importers.cdm')
logger.setLevel(logging.DEBUG)


def read_ccdh_model_yaml():
    yaml_url = 'https://raw.githubusercontent.com/cancerDHC/ccdhmodel/7d377740f17ad0cb1bf716483f64a55fd6fabf34/src/schema/ccdhmodel.yaml'
    r = requests.get(yaml_url)
    if r.status_code == 200:
        return r.content
    else:
        raise ValueError('Failed to fetch yaml from ' + yaml_url)


class CrdcHImporter:
    def __init__(self):
        pass

    @staticmethod
    def read_harmonized_attributes(yaml: str = read_ccdh_model_yaml()) -> Dict:
        model = yaml_loader.loads(yaml, target_class=YAMLRoot)
        harmonized_attributes = {}
        for cls in model.classes.values():
            for attribute in cls.get('attributes', {}).values():
                if attribute['range'] == 'CodeableConcept':
                    key = f'{model.name}.{cls["name"]}.{attribute["name"]}'
                    harmonized_attribute = {
                        'system': model.name, 'entity': cls["name"], 'attribute': attribute["name"],
                        'definition': attribute["description"], 'node_attributes': []
                    }
                    if "related_mappings" in attribute:
                        for m in attribute["related_mappings"]:
                            harmonized_attribute['node_attributes'].append(m)
                    harmonized_attributes[key] = harmonized_attribute
        return harmonized_attributes


    @staticmethod
    def read_harmonized_attributes_from_google_sheet(sheet_id: str, ranges: str) -> Dict:
        """
        Extract rows of CodeableConcept attributes from Google Drive
        :param str sheet_id: The identifier of the google sheet
        :param str ranges: ranges (tab) in the sheet
        :return: A list of adm values
        """
        harmonized_attributes = {}

        service = build('sheets', 'v4', credentials=authorize())

        # Call the Sheets API
        result = service.spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges=ranges).execute()
        value_ranges = result.get('valueRanges', [])
        for values in value_ranges[0]['values']:
            if len(values) < 9:
                continue
            elif values[7] != 'CodeableConcept':
                continue
            system, entity = values[4].strip().split('.')
            attribute = values[5].strip()
            key = f'{values[4].strip()}.{attribute}'
            if key not in harmonized_attributes:
                harmonized_attributes[key] = {'system': system, 'entity': entity, 'attribute': attribute,
                                              'definition': values[6].strip(), 'node_attributes': []}
            harmonized_attribute = harmonized_attributes[key]
            if len(values) > 13:
                for prop in values[12].split('\n'):
                    if len(prop.split('.')) != 3:
                        continue
                    harmonized_attribute['node_attributes'].append(prop.strip())
        return harmonized_attributes
