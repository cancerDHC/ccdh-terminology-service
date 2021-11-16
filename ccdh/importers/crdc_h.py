"""Importer for CRDC-H Model"""
import json
import logging

import requests
from typing import Dict

from linkml_runtime.loaders import yaml_loader
from linkml_runtime.utils.yamlutils import YAMLRoot

from ccdh.config import get_settings, neo4j_graph


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
        mapping_types = [
            # 'close_mappings',
            # 'related_mappings',
            'exact_mappings']
        # err_msg = 'Tried to use model.classes as a dictionary ' \
        #     'object while it was actually a jsonObj.\n'

        # Execution
        model: YAMLRoot = yaml_loader.loads(yaml, target_class=YAMLRoot)
        model_name = str(model.name)

        # native_class_dict: Ideally, would use dict(model.classes).values, but got error:
        # ... "{ValueError}dictionary update sequence element #0 has length 11; 2 is required" - jef 2021/07/29
        # noinspection PyProtectedMember
        native_class_dict: Dict = model.classes._as_dict

        # standard_class_dict: This is done primarily to convert instances of `enhanced_str` to
        # ...`str`. This solves an issue where Neo4J refused to import `enhanced_str`s.
        # ...We could use a simple recursive algorithm as in the following issue, but this `json`
        # ...module based approach is simple and reliable. - joeflack4 2021/11/01
        # https://stackoverflow.com/questions/54565160/how-to-convert-all-values-of-a-nested-dictionary-into-strings/54565257
        standard_class_dict: Dict = json.loads(json.dumps(native_class_dict))

        class_values = standard_class_dict.values()  # dict_values
        harmonized_attributes = {}
        for cls in class_values:
            for attribute in cls.get('attributes', {}).values():
                key = f'{model_name}.{cls["name"]}.{attribute["name"]}'
                harmonized_attribute = {
                    'system': model_name,
                    'entity': cls["name"],
                    'attribute': attribute["name"],
                    'definition': attribute["description"],
                    'node_attributes': []
                }
                for mapping in mapping_types:
                    if mapping in attribute:
                        for m in attribute[mapping]:
                            harmonized_attribute['node_attributes'].append(m)
                harmonized_attributes[key] = harmonized_attribute

        logger.info("Parsed the content in the CCDH Model YAML")
        return harmonized_attributes


if __name__ == '__main__':
    from ccdh.importers.importer import Importer
    Importer(neo4j_graph()).import_harmonized_attributes(
        CrdcHImporter.read_harmonized_attributes())
