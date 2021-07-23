import logging

import requests
import sys
from typing import Dict

from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.yamlutils import YAMLRoot

from ccdh.config import get_settings


logger = logging.getLogger('ccdh.importers.crcd_h')


def read_ccdh_model_yaml():
    branch = get_settings().ccdhmodel_branch
    yaml_url = f'https://raw.githubusercontent.com/cancerDHC/ccdhmodel/{branch}/src/schema/ccdhmodel.yaml'
    logger.info("Retrieving CCDH Model YAML: " + yaml_url)
    r = requests.get(yaml_url)
    if r.status_code == 200:
        return r.content
    else:
        logger.info(f"Failed to Retrieving CCDH Model YAML: {r.status_code}")
        logger.info(r.content)
        raise ValueError('Failed to fetch yaml from ' + yaml_url)


class CrdcHImporter:
    def __init__(self):
        pass

    @staticmethod
    def read_harmonized_attributes(yaml: str = read_ccdh_model_yaml()) -> Dict:
        """
        Extract the attributes from the ccdhmodel YAML
        :param yaml:
        :return: a dictionary of the attributes.
        """
        model = yaml_loader.loads(yaml, target_class=YAMLRoot)
        harmonized_attributes = {}
        try:
            class_values = model.classes.values()
        except AttributeError as err:
            print('Warning: Tried to use model.classes as a dictionary object '
                  'while it was actually a jsonObj.', file=sys.stderr)
            print(err, file=sys.stderr)
            class_values = model.classes._as_dict.values()
        for cls in class_values:
            for attribute in cls.get('attributes', {}).values():
                if attribute['range'] == f'enum_CCDH_{cls["name"]}_{attribute["name"]}':
                    key = f'{model.name}.{cls["name"]}.{attribute["name"]}'
                    harmonized_attribute = {
                        'system': model.name, 'entity': cls["name"], 'attribute': attribute["name"],
                        'definition': attribute["description"], 'node_attributes': []
                    }
                    if "exact_mappings" in attribute:
                        for m in attribute["exact_mappings"]:
                            harmonized_attribute['node_attributes'].append(m)
                    # if "related_mappings" in attribute:
                    #     for m in attribute["related_mappings"]:
                    #         harmonized_attribute['node_attributes'].append(m)
                    # harmonized_attribute['node_attributes'] = list(set(harmonized_attribute['node_attributes']))
                    harmonized_attributes[key] = harmonized_attribute
        logger.info("Parsed the content in the CCDH Model YAML")
        return harmonized_attributes
