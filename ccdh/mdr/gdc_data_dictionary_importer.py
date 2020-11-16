import csv
import sys
from pathlib import Path
from typing import List

from py2neo import Subgraph, Relationship
from sssom.io import *

from ccdh.config import ROOT_DIR, neo4j_graph
from ccdh.mdr.mdr_graph import MdrGraph

GDC_DIR = Path(__file__).parent.parent.parent / 'crdc-nodes/gdcdictionary'
sys.path.append(str(GDC_DIR))

from gdcdictionary.python import GDCDictionary
from ccdh.gdc import gdc_ncit_mappings


class GdcDataDictionaryImporter:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.gdc_dictionary = GDCDictionary()
        self.mdr_graph = MdrGraph(graph)

    def add_data_element(self, entity, attribute, commit=False) -> Subgraph:
        context = 'GDC'
        de_node = self.mdr_graph.get_data_element(context, entity, attribute)
        if de_node is None:
            de_node = self.mdr_graph.create_data_element(context, entity, attribute)
        subgraph = Subgraph([de_node])

        yaml_file = f'{entity.lower()}.yaml'
        if yaml_file not in self.gdc_dictionary.resolvers:
            print(f'GDC | {entity} not found')
            return None
        props = self.gdc_dictionary.resolvers[yaml_file].source.get('properties', {})
        if attribute not in props:
            print(f'GDC | {entity} | {attribute} not found')
            return None

        gdc_ncit_map = gdc_ncit_mappings()
        enum_values = props[attribute].get('enum', [])

        vd_node = self.mdr_graph.create_value_domain(enum_values)
        subgraph |= vd_node
        subgraph |= Relationship(vd_node, 'DOMAIN_OF', de_node)

        value_to_ncit_mapping = gdc_ncit_map.get(attribute, {})
        for value in enum_values:
            pv_node = self.mdr_graph.create_permissible_value(value)
            subgraph |= pv_node
            subgraph |= Relationship(pv_node, 'PART_OF', vd_node)

            map_row = value_to_ncit_mapping.get(value, None)
            if map_row:
                code, display = map_row[0:2]
                code_system = 'NCIT'
                vm_node = self.mdr_graph.find_value_meaning(code, code_system)
                if vm_node is None:
                    vm_node = self.mdr_graph.create_value_meaning(code, code_system, display)
                    subgraph |= vm_node
                subgraph |= Relationship(vm_node, 'MEANING_OF', pv_node)

        if commit:
            tx = self.graph.begin()
            tx.create(subgraph)
            tx.commit()
        return de_node, subgraph


def read_mvp_tsv() -> List[str]:
    rows = list()
    with open(ROOT_DIR / 'output/CDA_MVP_V0_value_sets-20-10-22.tsv', 'r') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)
        for row in reader:
            rows.append(row)
    return rows


def import_mvp():
    # rows = gdc_values(cdm_dictionary_sheet('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4'))
    rows = read_mvp_tsv()
    importer = GdcDataDictionaryImporter(neo4j_graph())
    mdr_graph = MdrGraph(neo4j_graph())
    data_elements = dict()
    for row in rows:
        if row[0].startswith('GDC'):
            data_elements[row[0]] = row[3]
    for gdc_tuple, cdm_tuple in data_elements.items():
        _, entity, attribute = gdc_tuple.split('.')
        de_node, subgraph = importer.add_data_element(entity, attribute, commit=False)
        _, object_class, prop = cdm_tuple.split('.')
        dec_node = mdr_graph.find_data_element_concept(object_class, prop)
        if dec_node is None:
            dec_node = mdr_graph.create_data_element_concept(object_class, prop)
        subgraph |= dec_node
        subgraph |= Relationship(de_node, 'REPRESENTS', dec_node)
        tx = neo4j_graph().begin()
        tx.create(subgraph)
        tx.commit()


if __name__ == '__main__':
    import_mvp()