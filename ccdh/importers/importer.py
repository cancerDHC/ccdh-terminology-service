from typing import List, Dict
import logging
import sys

from prefixcommons import contract_uri
from py2neo import Graph, Subgraph, Relationship
from sssom import MappingSet, Mapping

from ccdh.api.utils import decode_uri

from ccdh.config import neo4j_graph
from ccdh.importers.crdc_h import CrdcHImporter
from ccdh.importers.gdc import GdcImporter
from ccdh.importers.pdc import PdcImporter
from ccdh.db.mdr_graph import MdrGraph
from ccdh.namespaces import NAMESPACES, NCIT, SKOS

logger = logging.getLogger('ccdh.importers.importer')


class Importer:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.mdr_graph = MdrGraph(graph)

    def import_node_attribute(self, node_attribute):
        entity = node_attribute['entity']
        attribute = node_attribute['attribute']
        system = node_attribute['system']
        logger.info(f'Importing NodeAttribute {system}.{entity}.{attribute} ...')

        na_node = self.mdr_graph.get_node_attribute(system, entity, attribute)
        if na_node is not None:  # already exists. Skip
            # TODO: Update the node
            return

        na_node = self.mdr_graph.create_node_attribute(system, entity, attribute)
        na_node['definition'] = node_attribute['definition']
        if 'cadsr_cde' in node_attribute:
            na_node['reference'] = f'https://cdebrowser.nci.nih.gov/cdebrowserClient/cdeBrowser.html#/search?version=2.0&publicId={node_attribute["cadsr_cde"]}'
        subgraph = Subgraph([na_node])

        permissible_values = node_attribute['permissible_values']
        enum_node = self.mdr_graph.create_enumeration()
        subgraph |= enum_node
        subgraph |= Relationship(na_node, 'USES', enum_node)

        for value, description in permissible_values.items():
            pv_node = self.mdr_graph.create_permissible_value(value, description)
            subgraph |= pv_node
            subgraph |= Relationship(enum_node, 'HAS_PERMISSIBLE_VALUE', pv_node)

        tx = self.graph.begin()
        tx.create(subgraph)
        self.graph.commit(tx)

        logger.info(f'Importing {system}.{entity}.{attribute} was successful')

    def import_node_attributes(self, node_attributes: Dict[str, Dict]):
        for key, node_attribute in node_attributes.items():
            self.import_node_attribute(node_attribute)

    def import_harmonized_attributes(self, harmonized_attributes: Dict[str, Dict]):
        logger.info("Importing CRDC-H model -- started")
        for key, harmonized_attribute in harmonized_attributes.items():
            self.import_harmonized_attribute(harmonized_attribute)
        logger.info("Processed attributes: " + str(len(harmonized_attributes)))
        logger.info("Importing CRDC-H model -- completed")

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
                try:
                    system, entity_attribute = node_attribute.split(':')
                    entity, attribute = entity_attribute.split('.')
                except ValueError as e:
                    logger.error(f'Failed to parse the mapping attribute name: {node_attribute}')
                    logger.error(e)
                    continue
                na_node = self.mdr_graph.get_node_attribute(system, entity, attribute)
                if na_node is None:
                    logger.warning(node_attribute + ' not found in database')
                else:
                    subgraph |= Relationship(na_node, 'MAPS_TO', ha_node)

        tx = self.graph.begin()
        tx.create(subgraph)
        self.graph.commit(tx)

        logger.info(f'Importing HarmonizedAttribute {system}.{entity}.{attribute} was successful')

    def import_ncit_mapping(self, gdc_ncit_mappings, system):
        query = '''
        MATCH (cs:CodeSet:Resource)<-[:HAS_MEANING]-
          (:HarmonizedAttribute)<-[:MAPS_TO]-
          (:NodeAttribute {system: $system, attribute: $attribute})-[:USES]->
          (:Enumeration)-[:HAS_PERMISSIBLE_VALUE]->(pv:PermissibleValue {pref_label: $pv_label})
        MATCH (cr:ConceptReference:Resource {uri: $cr_uri})
        MERGE (cr)<-[:MAPPED_TO]-(m:Mapping:Resource)-[:MAPPED_FROM]->(pv)
        ON CREATE SET m.predicate_id = $predicate_id, m.creator_id = $creator_id
        ON MATCH SET m.predicate_id = $predicate_id, m.creator_id = $creator_id
        MERGE (cs)-[:HAS_MEMBER]->(cr)
        RETURN cr
        '''
        for _, attr in gdc_ncit_mappings.items():
            for _, value in attr.items():
                code, _pref_label, predicate_id, attribute, pv_label = list(value[0:5])
                if predicate_id == 'Has Synonym':
                    predicate_id = SKOS.exactMatch
                elif predicate_id == 'Related To':
                    predicate_id = SKOS.relatedMatch
                params = {
                    'system': system,
                    'attribute': attribute,
                    'predicate_id': predicate_id,
                    'pv_label': pv_label,
                    'creator_id': 'https://gdc.cancer.gov',
                    'cr_uri': f'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#{code}',
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
            MATCH (cd:CodeSet:Resource)<-[:HAS_MEANING]-
              (c:HarmonizedAttribute {system: $dec_system, entity: $dec_entity, attribute: $dec_attribute})<-[:MAPS_TO]-
              (de:NodeAttribute {system: $de_system, entity: $entity, attribute: $attribute})-[:USES]->
              (vd:Enumeration)-[:HAS_PERMISSIBLE_VALUE]->(pv:PermissibleValue {pref_label: $pv_pref_label})
            MERGE (cr:ConceptReference:Resource {uri: $cr_uri})
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

    def import_ncit(self):
        # CALL 'n10s.rdf.import.fetch("file:///var/lib/neo4j/import/ncit-termci.ttl", "Turtle", {predicateExclusionList : [ "https://hotecosystem.org/termci/contents"] })'
        self.graph.call('n10s.rdf.import.fetch', "file:///var/lib/neo4j/import/ncit-termci.ttl", "Turtle",
                        {'predicateExclusionList': ["https://hotecosystem.org/termci/contents"]})


if __name__ == '__main__':
    Importer(neo4j_graph()).import_ncit()
    Importer(neo4j_graph()).import_node_attributes(PdcImporter.read_data_dictionary())
    Importer(neo4j_graph()).import_node_attributes(GdcImporter.read_data_dictionary())
    Importer(neo4j_graph()).import_harmonized_attributes(CrdcHImporter.read_harmonized_attributes())
    Importer(neo4j_graph()).import_ncit_mapping(GdcImporter.read_ncit_mappings(), 'GDC')
    Importer(neo4j_graph()).import_ncit_mapping(GdcImporter.read_ncit_mappings(), 'PDC')
