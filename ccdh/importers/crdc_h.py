"""Importer for CRDC-H Model"""
import logging
import requests
from typing import Dict

from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.yamlutils import YAMLRoot

from ccdh.config import get_settings


logger = logging.getLogger('ccdh.importers.crcd_h')


def read_ccdh_model_yaml():
    """Read model yaml from CCDH Model GH repository"""
    branch = get_settings().ccdhmodel_branch
    yaml_url = f'https://raw.githubusercontent.com/cancerDHC/ccdhmodel/' \
               f'{branch}/model/schema/crdch_model.yaml'
    logger.info("Retrieving CCDH Model YAML: " + yaml_url)
    r = requests.get(yaml_url)
    if r.status_code == 200:
        return r.content
    else:
        logger.info(f"Failed to Retrieving CCDH Model YAML: {r.status_code}")
        logger.info(r.content)
        raise ValueError('Failed to fetch yaml from ' + yaml_url)


class CrdcHImporter:
    """CRDC (Cancer Research Data Commons) Harmonization Importer"""
    def __init__(self):
        pass

    @staticmethod
    def read_harmonized_attributes(yaml: str = None) -> Dict:
        """
        Extract the attributes from the ccdhmodel YAML
        :param yaml:
        :return: a dictionary of the attributes.
        """
        if yaml is None:
            yaml = read_ccdh_model_yaml()
        # Variables
        # close/related disabled: We've heard these mappings will all soon be
        # merged. - jef 2021/07/26
        mapping_types = (
            # 'close_mappings',
            # 'related_mappings',
            'exact_mappings')
        err_msg = 'Tried to use model.classes as a dictionary ' \
            'object while it was actually a jsonObj.\n'

        # Execution
        model = yaml_loader.loads(yaml, target_class=YAMLRoot)
        harmonized_attributes = {}
        # Ideally, would use dict(model.classes).values, but got error:
        # ... "{ValueError}dictionary update sequence element #0 has length 11; 2 is required" - jef 2021/07/29
        # noinspection PyProtectedMember
        class_values = model.classes._as_dict.values()
        for cls in class_values:
            for attribute in cls.get('attributes', {}).values():
                key = f'{model.name}.{cls["name"]}.{attribute["name"]}'
                harmonized_attribute = {
                    'system': model.name,
                    'entity': cls["name"],
                    'attribute': attribute["name"],
                    'definition': attribute["description"],
                    'node_attributes': []
                }
                for mapping in mapping_types:
                    if mapping in attribute:
                        for m in attribute[mapping]:
                            harmonized_attribute['node_attributes'].append(m)
                # harmonized_attribute['node_attributes'] = \
                #     list(set(harmonized_attribute['node_attributes']))
                harmonized_attributes[key] = harmonized_attribute

        logger.info("Parsed the content in the CCDH Model YAML")
        return harmonized_attributes
