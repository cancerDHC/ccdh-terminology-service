import csv
import sys
from pathlib import Path
from typing import List

from py2neo import Subgraph, Relationship
from sssom.io import *

from ccdh.config import ROOT_DIR, neo4j_graph
from ccdh.db.mdr_graph import MdrGraph
from ccdh.gdc import gdc_ncit_mappings

GDC_DIR = Path(__file__).parent.parent.parent / 'crdc-nodes/gdcdictionary'
sys.path.append(str(GDC_DIR))

from gdcdictionary.python import GDCDictionary


class GdcDataDictionaryImporter:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.gdc_dictionary = GDCDictionary()
        self.mdr_graph = MdrGraph(graph)

    def add_node_attribute(self, entity, attribute, commit=False) -> Subgraph:
        system = 'GDC'
        node_attribute = self.mdr_graph.get_node_attribute(system, entity, attribute)
        if node_attribute is None:
            node_attribute = self.mdr_graph.create_node_attribute(system, entity, attribute)
        subgraph = Subgraph([node_attribute])

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
        node_attribute['definition'] = props[attribute].get('description', '')

        vd_node = self.mdr_graph.create_enumeration()
        subgraph |= vd_node
        subgraph |= Relationship(node_attribute, 'USES', vd_node)

        value_to_ncit_mapping = gdc_ncit_map.get(attribute, {})
        code_nodes = {}
        for value in enum_values:
            pv_node = self.mdr_graph.create_permissible_value(value)
            subgraph |= pv_node
            subgraph |= Relationship(vd_node, 'HAS_MEMBER', pv_node)

            map_row = value_to_ncit_mapping.get(value, None)
            if map_row:
                code, definition = map_row[0:2]
                scheme = 'https://bioportal.bioontology.org/ontologies/NCIT'
                uri = f'NCIT:{code}'
                vm_node = self.mdr_graph.find_concept_reference(code, scheme)
                if vm_node is None:
                    vm_node = code_nodes.get(uri, self.mdr_graph.create_concept_reference(uri, code, scheme, definition))
                    code_nodes[uri] = vm_node
                    subgraph |= vm_node
                subgraph |= Relationship(pv_node, 'HAS_MEANING', vm_node)

        if commit:
            tx = self.graph.begin()
            tx.create(subgraph)
            tx.commit()
        return node_attribute, subgraph

    def import_mvp(self):
        # rows = gdc_values(cdm_dictionary_sheet('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4'))
        rows = GdcDataDictionaryImporter.read_mvp_tsv()
        importer = GdcDataDictionaryImporter(self.graph)
        node_attributes = dict()
        for row in rows:
            if row[0].startswith('GDC'):
                node_attributes[row[0]] = row[3]
        for gdc_tuple, cdm_tuple in node_attributes.items():
            _, entity, attribute = gdc_tuple.split('.')
            de_node, subgraph = importer.add_node_attribute(entity, attribute, commit=False)
            _, dec_entity, dec_attribute = cdm_tuple.split('.')
            dec_node = self.mdr_graph.find_harmonized_attribute(dec_entity, dec_attribute)
            if dec_node is None:
                dec_node = self.mdr_graph.create_harmonized_attribute(dec_entity, dec_attribute)
                subgraph |= dec_node
            subgraph |= Relationship(dec_node, 'HAS_REPRESENTATION', de_node)
            tx = neo4j_graph().begin()
            tx.create(subgraph)
            tx.commit()

    @staticmethod
    def read_mvp_tsv() -> List[str]:
        rows = list()
        with open(ROOT_DIR / 'output/CDA_MVP_V0_value_sets-20-10-22.tsv', 'r') as tsvfile:
            reader = csv.reader(tsvfile, delimiter='\t')
            next(reader)
            for row in reader:
                rows.append(row)
        return rows

    def import_gdc_data_dictionary(category: str):
        pass


if __name__ == '__main__':
    GdcDataDictionaryImporter(neo4j_graph()).import_mvp()
