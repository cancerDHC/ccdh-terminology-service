from typing import List
import logging
from py2neo import Graph, Subgraph, Relationship
from sssom import Mapping

from ccdh.config import neo4j_graph
from ccdh.importers.gdc import GdcImporter
from ccdh.importers.pdc import PdcImporter
from ccdh.mdr.mdr_graph import MdrGraph

logger = logging.getLogger('ccdh.importers')
logger.setLevel(logging.DEBUG)


class Importer:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.mdr_graph = MdrGraph(graph)

    def import_data_element(self, data_element):
        entity = data_element['entity']
        attribute = data_element['attribute']
        context = data_element['context']
        logger.info(f'Importing DataElement {context}.{entity}.{attribute} ...')

        de_node = self.mdr_graph.get_data_element(context, entity, attribute)
        if de_node is not None:  # already exists. Skip
            return

        de_node = self.mdr_graph.create_data_element(context, entity, attribute)
        de_node['definition'] = data_element['definition']
        subgraph = Subgraph([de_node])

        permissible_values = data_element['permissible_values']
        vd_node = self.mdr_graph.create_value_domain()
        subgraph |= vd_node
        subgraph |= Relationship(de_node, 'USES', vd_node)

        for value in permissible_values:
            pv_node = self.mdr_graph.create_permissible_value(value)
            subgraph |= pv_node
            subgraph |= Relationship(vd_node, 'HAS_MEMBER', pv_node)

        tx = self.graph.begin()
        tx.create(subgraph)
        tx.commit()

        logger.info(f'Importing {context}.{entity}.{attribute} was successful')

    def import_data_elements(self, data_elements: List):
        for key, data_element in data_elements.items():
            self.import_data_element(data_element)

    def add_data_element_concept(self, data_element_concept):
        context = data_element_concept['context']
        object_class = data_element_concept['objectClass']
        proprty = data_element_concept['property']

        logger.info(f'Importing DataElementConcpet {context}.{object_class}.{proprty} ...')

        dec_node = self.mdr_graph.get_data_element_concept(context, object_class, property)

        if dec_node is not None:  # already exists. Skip
            return

        dec_node = self.mdr_graph.create_data_element_concept(context, object_class, property)
        dec_node['definition'] = data_element_concept['definition']
        subgraph = Subgraph([dec_node])

        cd_node = self.mdr_graph.create_conceptual_domain()
        subgraph |= cd_node
        subgraph |= Relationship(dec_node, 'USES', cd_node)

        tx = self.graph.begin()
        tx.create(subgraph)
        tx.commit()

        logger.info(f'Importing DataElementConcpet {context}.{object_class}.{proprty} was successful')

    def import_mapping(self, mapping: Mapping):
        context, entity, attribute = mapping.subject_field.split(',')
        permissible_value = mapping.subject_label
        object_id = mapping.object_id
        
        


if __name__ == '__main__':
    Importer(neo4j_graph()).import_data_elements(PdcImporter.read_data_dictionary())
