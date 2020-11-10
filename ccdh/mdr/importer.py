import sys
from collections import namedtuple
from typing import List
from py2neo import Graph

from ccdh.mdr.models import *
from pathlib import Path
from urllib.parse import quote_plus

GDC_DIR = Path(__file__).parent.parent.parent / 'crdc-nodes/gdcdictionary'
sys.path.append(str(GDC_DIR))

from gdcdictionary.python import GDCDictionary
from ccdh.gdc import gdc_ncit_mappings

MOD_DIR = GDC_DIR / 'gdcdictionary'
MAP_DIR = Path(__file__).parent.parent.parent / 'mappings/gdc-ncit'

ResolverPair = namedtuple('ResolverPair', ['resolver', 'source'])


class GdcImporter:
    def __init__(self, graph: Graph):
        self.gdc = GDCDictionary()
        self.graph = graph

    def add_data_element(self, entity, attribute) -> List[Model]:
        where_stmt = f"_.context='GDC' and _.entity='{entity}' and _.attribute='{attribute}'"
        data_element = DataElement.match(self.graph).where(where_stmt).first()
        if data_element is not None:
            return data_element

        tx = self.graph.begin()
        yaml_file = f'{entity.lower()}.yaml'
        if yaml_file not in self.gdc.resolvers:
            print(f'GDC | {entity} not found')
            return None
        props = self.gdc.resolvers[yaml_file].source.get('properties', {})
        if attribute not in props:
            print(f'GDC | {entity} | {attribute} not found')
            return None
        data_element = DataElement(identifier=f'http://ccdh/data_element/gdc/{entity}/{attribute}',
                                   entity=entity, attribute=attribute, context='GDC')

        tx.create(data_element)

        value_domain = ValueDomain(identifier=f'http://ccdh/value_domain/gdc/{entity}/{attribute}')
        value_domain.data_element.add(data_element)
        tx.create(value_domain)

        gdc_ncit_map = gdc_ncit_mappings()
        enum_values = props[attribute].get('enum', [])
        for value in enum_values:
            identifier = f'http://ccdh/permissible_value/gdc/{entity}/{attribute}{quote_plus(value)}'
            pv = PermissibleValue(identifier=identifier, value=value)
            pv.value_domain.add(value_domain)

            map_row = gdc_ncit_map.get(attribute, {}).get(value, [])
            if map_row:
                code, display = map_row[0:2]
                code_system = 'NCIT'
                match_str = f"_.code = '{map_row[0]}' and _.code_system = '{code_system}'"
                vm = ValueMeaning.match(self.graph).where(match_str).first()
                if vm is None:
                    vm = ValueMeaning(identifier=f'{code_system}:{code}', display=display, code=code,
                                      code_system=code_system)
                    tx.create(vm)
                pv.value_meaning.add(vm)
            tx.create(pv)
        tx.commit()
        return data_element

    def add_data_element_concept(self, object_class, property):
        where_stmt = f"_.object_class='{object_class}' and _.property='{property}'"
        data_element_concept = DataElementConcept.match(self.graph).where(where_stmt).first()
        if data_element_concept is None:
            tx = self.graph.begin()
            identifier = f'http://ccdh/data_element_concept/{quote_plus(object_class)}/{property}'
            data_element_concept = DataElementConcept(identifier=identifier, name=f'{object_class}.{property}',
                                                      object_class=object_class, property=property)
            tx.create(data_element_concept)
            tx.commit()
        return data_element_concept

    def assign_data_element_concept(self, data_element: DataElement, data_element_concept: DataElementConcept):
        if len(data_element.data_element_concept) == 1:
            return
        tx = self.graph.begin()
        data_element.data_element_concept.add(data_element_concept)
        tx.merge(data_element)
        tx.commit()








