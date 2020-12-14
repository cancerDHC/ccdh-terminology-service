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
from ccdh.mdr.mdr_graph import MdrGraph
from ccdh.namespaces import NAMESPACES, NCIT

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

    def import_data_elements(self, data_elements: Dict[str, Dict]):
        for key, data_element in data_elements.items():
            self.import_data_element(data_element)

    def import_data_element_concepts(self, data_element_concepts: Dict[str, Dict]):
        for key, data_element_concept in data_element_concepts.items():
            self.import_data_element_concept(data_element_concept)

    def import_data_element_concept(self, data_element_concept):
        context = data_element_concept['context']
        object_class = data_element_concept['object_class']
        property = data_element_concept['property']

        logger.info(f'Importing DataElementConcpet {context}.{object_class}.{property} ...')

        dec_node = self.mdr_graph.get_data_element_concept(context, object_class, property)

        if dec_node is not None:  # already exists. Skip
            return

        dec_node = self.mdr_graph.create_data_element_concept(context, object_class, property)
        dec_node['definition'] = data_element_concept['definition']
        subgraph = Subgraph([dec_node])

        cd_node = self.mdr_graph.create_conceptual_domain()
        subgraph |= cd_node
        subgraph |= Relationship(dec_node, 'USES', cd_node)

        if 'data_elements' in data_element_concept:
            for data_element in data_element_concept['data_elements']:
                context, entity, attribute = data_element.split('.')
                de_node = self.mdr_graph.get_data_element(context, entity, attribute)
                if de_node is None:
                    print(data_element + ' not found in database')
                else:
                    subgraph |= Relationship(de_node, 'HAS_MEANING', dec_node)

        tx = self.graph.begin()
        tx.create(subgraph)
        tx.commit()

        logger.info(f'Importing DataElementConcpet {context}.{object_class}.{property} was successful')

    def import_gdc_ncit_mapping(self, gdc_ncit_mappings):
        query = '''
        MATCH (cd:ConceptualDomain:Resource:CodeSet)<-[:USES]-
          (c:DataElementConcept)<-[:HAS_MEANING]-
          (de:DataElement {context: 'GDC', attribute: $attribute})-[:USES]->
          (vd:ValueDomain)-[:HAS_MEMBER]->(p:PermissibleValue {pref_label: $pv_pref_label})
        MERGE (vm:ValueMeaning:Resource:Concept {uri: $vm_uri})
        ON CREATE SET vm.pref_label = $vm_pref_label, vm.notation = $vm_notation, vm.scheme = $vm_in_scheme
        ON MATCH SET vm.pref_label = $vm_pref_label, vm.notation = $vm_notation, vm.scheme = $vm_in_scheme
        MERGE (p)<-[rpr:HAS_REPRESENTATION]-(vm)
        ON CREATE SET rpr.predicate_id = $predicate_id, rpr.creator_id = 'http://gdc.cancer.gov'
        ON MATCH SET rpr.predicate_id = $predicate_id, rpr.creator_id = 'http://gdc.cancer.gov'
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
        de_context, entity, attribute = mapping.subject_match_field.split('.')
        dec_context, object_class, prop = mapping.object_match_field.split('.')
        curie = mapping.object_id
        if curie:  # not mapped
            print(curie)
            in_scheme, notation = curie.split(':')
            vm_uri = decode_uri(mapping.object_id)
            query = '''
            MATCH (cd:ConceptualDomain:Resource:CodeSet)<-[:USES]-
              (c:DataElementConcept {context: $dec_context, object_class: $object_class, property: $property})<-[:HAS_MEANING]-
              (de:DataElement {context: $de_context, entity: $entity, attribute: $attribute})-[:USES]->
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
                'dec_context': dec_context,
                'entity': entity,
                'attribute': attribute,
                'de_context': de_context,
                'object_class': object_class,
                'property': prop,
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
                      (c:DataElementConcept {context: $dec_context, object_class: $object_class, property: $property})<-[:HAS_MEANING]-
                      (de:DataElement {context: $de_context, entity: $entity, attribute: $attribute})-[:USES]->
                      (vd:ValueDomain)-[:HAS_MEMBER]->(p:PermissibleValue {pref_label: $pv_pref_label})
                    SET p.comment = CASE EXISTS(p.comment) WHEN True THEN p.comment + $comment else [$comment] END
                    '''
                params = {
                    'dec_context': dec_context,
                    'entity': entity,
                    'attribute': attribute,
                    'de_context': de_context,
                    'object_class': object_class,
                    'property': prop,
                    'predicate_id': mapping.predicate_id,
                    'pv_pref_label': mapping.subject_label,
                    'comment': mapping.comment,
                }
                self.graph.run(query, **params)


if __name__ == '__main__':
    Importer(neo4j_graph()).import_data_elements(PdcImporter.read_data_dictionary())
    Importer(neo4j_graph()).import_data_elements(GdcImporter.read_data_dictionary())
    Importer(neo4j_graph()).import_data_element_concepts(CdmImporter.read_data_element_concepts(CDM_GOOGLE_SHEET_ID, 'MVPv0'))

    Importer(neo4j_graph()).import_gdc_ncit_mapping(GdcImporter.read_ncit_mappings())
