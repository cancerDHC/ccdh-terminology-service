from typing import List, Dict
import logging

from prefixcommons import contract_uri
from py2neo import Graph, Subgraph, Relationship
from sssom import MappingSet, Mapping

from ccdh.api.utils import decode_uri

from ccdh.config import neo4j_graph, CDM_GOOGLE_SHEET_ID
from ccdh.importers.cdm import CdmImporter
from ccdh.importers.gdc import GdcImporter
from ccdh.importers.pdc import PdcImporter
from ccdh.db.mdr_graph import MdrGraph
from ccdh.namespaces import NAMESPACES, NCIT

logger = logging.getLogger('ccdh.importers')
logger.setLevel(logging.DEBUG)


class Importer:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.mdr_graph = MdrGraph(graph)

    def import_node_attribute(self, node_attribute):
        entity = node_attribute['entity']
        attribute = node_attribute['attribute']
        system = node_attribute['system']
        logger.info(f'Importing DataElement {system}.{entity}.{attribute} ...')

        na_node = self.mdr_graph.get_node_attribute(system, entity, attribute)
        if na_node is not None:  # already exists. Skip
            return

        na_node = self.mdr_graph.create_node_attribute(system, entity, attribute)
        na_node['definition'] = node_attribute['definition']
        subgraph = Subgraph([na_node])

        permissible_values = node_attribute['permissible_values']
        enum_node = self.mdr_graph.create_enumeration()
        subgraph |= enum_node
        subgraph |= Relationship(na_node, 'USES', enum_node)

        for value in permissible_values:
            pv_node = self.mdr_graph.create_permissible_value(value)
            subgraph |= pv_node
            subgraph |= Relationship(enum_node, 'HAS_PERMISSIBLE_VALUE', pv_node)

        tx = self.graph.begin()
        tx.create(subgraph)
        tx.commit()

        logger.info(f'Importing {system}.{entity}.{attribute} was successful')

    def import_node_attributes(self, node_attributes: Dict[str, Dict]):
        for key, node_attribute in node_attributes.items():
            self.import_node_attribute(node_attribute)

    def import_harmonized_attributes(self, harmonized_attributes: Dict[str, Dict]):
        for key, harmonized_attribute in harmonized_attributes.items():
            self.import_harmonized_attribute(harmonized_attribute)

    def import_harmonized_attribute(self, harmonized_attribute):
        system = harmonized_attribute['system']
        entity = harmonized_attribute['entity']
        attribute = harmonized_attribute['attribute']

        logger.info(f'Importing HarmonizedAttribute {system}.{entity}.{attribute} ...')

        ha_node = self.mdr_graph.get_harmonized_attribute(system, entity, attribute)

        if ha_node is not None:  # already exists. Skip
            return

        ha_node = self.mdr_graph.create_harmonized_attribute(system, entity, attribute)
        ha_node['definition'] = harmonized_attribute['definition']
        subgraph = Subgraph([ha_node])

        cs_node = self.mdr_graph.create_code_set()
        subgraph |= cs_node
        subgraph |= Relationship(ha_node, 'HAS_MEANING', cs_node)

        if 'node_attributes' in harmonized_attribute:
            for node_attribute in harmonized_attribute['node_attributes']:
                system, entity, attribute = node_attribute.split('.')
                na_node = self.mdr_graph.get_node_attribute(system, entity, attribute)
                if na_node is None:
                    print(node_attribute + ' not found in database')
                else:
                    subgraph |= Relationship(na_node, 'MAPS_TO', ha_node)

        tx = self.graph.begin()
        tx.create(subgraph)
        tx.commit()

        logger.info(f'Importing HarmonizedAttribute {system}.{entity}.{attribute} was successful')

    def import_gdc_ncit_mapping(self, gdc_ncit_mappings):
        query = '''
        MATCH (cd:CodeSet:Resource)<-[:HAS_MEANING]-
          (c:HarmonizedAttribute)<-[:MAPS_TO]-
          (de:NodeAttribute {system: 'GDC', attribute: $attribute})-[:USES]->
          (vd:Enumeration)-[:HAS_PERMISSIBLE_VALUE]->(p:PermissibleValue {pref_label: $pv_pref_label})
        MERGE (vm:ConceptReference:Resource {uri: $vm_uri})
        ON CREATE SET vm.pref_label = $vm_pref_label, vm.notation = $vm_notation, vm.defined_in = $vm_defined_in
        ON MATCH SET vm.pref_label = $vm_pref_label, vm.notation = $vm_notation, vm.defined_in = $vm_defined_in
        MERGE (p)<-[:MAPPED_FROM]-(m:Mapping)-[:MAPPED_TO]->(vm)
        ON CREATE SET m.predicate_id = $predicate_id, m.creator_id = 'https://gdc.cancer.gov'
        ON MATCH SET m.predicate_id = $predicate_id, m.creator_id = 'https://gdc.cancer.gov'
        MERGE (vm)<-[:HAS_MEMBER]-(cd)
        RETURN vm
        '''
        for _, attr in gdc_ncit_mappings.items():
            for _, value in attr.items():
                vm_notation, vm_pref_label, predicate_id, attribute, pv_pref_label = list(value[0:5])
                if predicate_id == 'Has Synonym':
                    predicate_id = 'skos:exactMatch'
                elif predicate_id == 'Related To':
                    predicate_id = 'skos:relatedMatch'
                params = {
                    'attribute': attribute,
                    'predicate_id': predicate_id,
                    'pv_pref_label': pv_pref_label,
                    'vm_pref_label': vm_pref_label,
                    'vm_notation': vm_notation,
                    'vm_in_scheme': 'NCIT',
                    'vm_uri': f'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#{vm_notation}',
                }
                self.graph.run(query, **params)

    def import_mapping_set(self, mapping_set: MappingSet, curie_map: Dict[str, str]):
        for mapping in mapping_set.mappings:
            self.import_mapping(mapping, curie_map)

    def import_mapping(self, mapping: Mapping, curie_map: Dict[str, str]):
        de_system, entity, attribute = mapping.subject_match_field.split('.')
        dec_system, dec_entity, dec_attribute = mapping.object_match_field.split('.')
        curie = mapping.object_id
        if curie:  # not mapped
            print(curie)
            in_scheme, notation = curie.split(':')
            vm_uri = decode_uri(mapping.object_id)
            query = '''
            MATCH (cd:ConceptualDomain:Resource:CodeSet)<-[:USES]-
              (c:DataElementConcept {system: $dec_system, entity: $dec_entity, attribute: $dec_attribute})<-[:HAS_MEANING]-
              (de:DataElement {system: $de_system, entity: $entity, attribute: $attribute})-[:USES]->
              (vd:ValueDomain)-[:HAS_MEMBER]->(p:PermissibleValue {pref_label: $pv_pref_label})
            MERGE (vm:ValueMeaning:Resource:Concept {uri: $vm_uri})
            ON CREATE SET vm.pref_label = $vm_pref_label, vm.notation = $vm_notation, vm.scheme = $vm_in_scheme
            ON MATCH SET vm.pref_label = $vm_pref_label, vm.notation = $vm_notation, vm.scheme = $vm_in_scheme
            MERGE (vm)<-[:HAS_MEMBER]-(cd)
            MERGE (p)<-[rpr:HAS_REPRESENTATION]-(vm)
            ON CREATE SET rpr.predicate_id = $predicate_id, rpr.creator_id = $creator_id, rpr.comment = $comment
            ON MATCH SET rpr.predicate_id = $predicate_id, rpr.creator_id = $creator_id, rpr.comment = $comment        
            '''
            params = {
                'dec_system': dec_system,
                'entity': entity,
                'attribute': attribute,
                'de_system': de_system,
                'dec_entity': dec_entity,
                'dec_attribute': dec_attribute,
                'predicate_id': mapping.predicate_id,
                'pv_pref_label': mapping.subject_label,
                'vm_pref_label': mapping.object_label,
                'vm_notation': notation,
                'vm_in_scheme': in_scheme,
                'vm_uri': vm_uri,
                'creator_id': mapping.creator_id,
                'comment': mapping.comment or '',
            }
            self.graph.run(query, **params)
        else:
            if mapping.comment:
                query = '''
                    MATCH (cd:ConceptualDomain:Resource:CodeSet)<-[:USES]-
                      (c:DataElementConcept {system: $dec_system, entity: $dec_entity, attribute: $dec_attribute})<-[:HAS_MEANING]-
                      (de:DataElement {system: $de_system, entity: $entity, attribute: $attribute})-[:USES]->
                      (vd:ValueDomain)-[:HAS_MEMBER]->(p:PermissibleValue {pref_label: $pv_pref_label})
                    SET p.comment = CASE EXISTS(p.comment) WHEN True THEN p.comment + $comment else [$comment] END
                    '''
                params = {
                    'dec_system': dec_system,
                    'entity': entity,
                    'attribute': attribute,
                    'de_system': de_system,
                    'dec_entity': dec_entity,
                    'dec_attribute': dec_attribute,
                    'predicate_id': mapping.predicate_id,
                    'pv_pref_label': mapping.subject_label,
                    'comment': mapping.comment,
                }
                self.graph.run(query, **params)


if __name__ == '__main__':
    Importer(neo4j_graph()).import_node_attributes(PdcImporter.read_data_dictionary())
    Importer(neo4j_graph()).import_node_attributes(GdcImporter.read_data_dictionary())
    # Importer(neo4j_graph()).import_harmonized_attributes(CdmImporter.read_harmonized_attributes(CDM_GOOGLE_SHEET_ID, 'MVPv0'))
    # Importer(neo4j_graph()).import_gdc_ncit_mapping(GdcImporter.read_ncit_mappings())
