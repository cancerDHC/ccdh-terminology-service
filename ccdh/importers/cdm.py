import logging
from typing import Dict
from googleapiclient.discovery import build
from ccdh.gdrive.authorize import authorize

logger = logging.getLogger('ccdh.importers.cdm')
logger.setLevel(logging.DEBUG)


class CdmImporter:
    def __init__(self):
        pass

    @staticmethod
    def read_data_element_concepts(sheet_id: str, ranges: str) -> Dict:
        """
        Extract rows of CodeableConcept attributes from Google Drive
        :param str sheet_id: The identifier of the google sheet
        :param str ranges: ranges (tab) in the sheet
        :return: A list of adm values
        """
        data_element_concepts = {}

        service = build('sheets', 'v4', credentials=authorize())

        # Call the Sheets API
        result = service.spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges=ranges).execute()
        value_ranges = result.get('valueRanges', [])
        for values in value_ranges[0]['values']:
            if len(values) < 9:
                continue
            elif values[7] != 'CodeableConcept':
                continue
            context, entity = values[4].strip().split('.')
            attribute = values[5].strip()
            key = f'{values[4].strip()}.{attribute}'
            if key not in data_element_concepts:
                data_element_concepts[key] = {'context': context, 'object_class': entity, 'property': attribute,
                                              'definition': values[6].strip(), 'data_elements': []}
            data_element_concept = data_element_concepts[key]
            if len(values) > 13:
                for prop in values[12].split('\n'):
                    if len(prop.split('.')) != 3:
                        continue
                    data_element_concept['data_elements'].append(prop.strip())
        return data_element_concepts






