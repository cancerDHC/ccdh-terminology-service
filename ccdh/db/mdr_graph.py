from typing import List, Union, Tuple
from urllib.parse import quote_plus

import shortuuid
from py2neo import Relationship, Node, NodeMatcher, Subgraph, Graph
from py2neo.cypher import Cursor
from sssom.sssom_datamodel import MappingSet
from prefixcommons import expand_uri, contract_uri

# from ccdh.config import DEFAULT_PAGE_SIZE
from ccdh.api.utils import uri_to_curie, curie_to_uri
from ccdh.db.models import *

from ccdh.namespaces import CCDH, GDC, PDC, NAMESPACES

DEFAULT_PAGE_SIZE = 25


class MdrGraph:
    def __init__(self, graph: Graph):
        self.graph = graph

    @staticmethod
    def create_node_attribute_uri(system: str, entity: str, attr: str) -> str:
        return str(CCDH[f'node-attributes/{quote_plus(system)}/{quote_plus(entity)}/{quote_plus(attr)}'])

    @staticmethod
    def create_enumeration_uri():
        return str(CCDH[f'enumerations/{shortuuid.uuid()}'])

    @staticmethod
    def create_harmonized_attribute_uri(system, entity, attribute):
        return str(CCDH[f'harmonized-attributes/{quote_plus(system)}/{quote_plus(entity)}/{quote_plus(attribute)}'])

    @staticmethod
    def create_permissible_value_uri():
        return str(CCDH[f'permissible-values/{shortuuid.uuid()}'])

    @staticmethod
    def create_code_set_uri():
        return str(CCDH[f'code-sets/{shortuuid.uuid()}'])

    @staticmethod
    def create_code_set() -> Node:
        uri = MdrGraph.create_code_set_uri()
        return Node('CodeSet', 'Resource', uri=uri)

    @staticmethod
    def create_node_attribute(system: str, entity: str, attr: str) -> Node:
        uri = MdrGraph.create_node_attribute_uri(system, entity, attr)
        return Node('NodeAttribute', 'Resource', uri=uri, entity=entity, attribute=attr, system=system)

    @staticmethod
    def create_enumeration() -> Tuple[Subgraph]:
        uri = MdrGraph.create_enumeration_uri()
        return Node('Enumeration', 'Resource', uri=uri)

    @staticmethod
    def create_concept_reference(uri, notation, defined_in, pref_label, version=None, is_curie=True):
        uri = expand_uri(uri, NAMESPACES) if is_curie else uri
        concept_reference = Node('ConceptReference', 'Resource', uri=uri, notation=notation,
                                 defined_in=defined_in, pref_label=pref_label, version=version)
        return concept_reference

    @staticmethod
    def create_permissible_value(value: str):
        uri = MdrGraph.create_permissible_value_uri()
        pv = Node('PermissibleValue', 'Resource', pref_label=value, uri=uri)
        return pv

    @staticmethod
    def create_harmonized_attribute(system, entity: str, attribute: str):
        uri = MdrGraph.create_harmonized_attribute_uri(system, entity, attribute)
        return Node('HarmonizedAttribute', 'Resource', uri=uri, system=system, entity=entity, attribute=attribute)

    @staticmethod
    def build_where_statement(node_str, **kwargs):
        where_list = [f"{node_str}.{key}='{kwargs[key]}'" for key in kwargs if kwargs[key] is not None]
        return ' AND '.join(where_list)

    @staticmethod
    def build_where_statement_case_insensitive(node_str, **kwargs):
        where_list = [f"{node_str}.{key} =~ '(?i){kwargs[key]}'" for key in kwargs if kwargs[key] is not None]
        return ' AND '.join(where_list)

    def get_resource_by_uri(self, uri: str) -> Node:
        return NodeMatcher(self.graph).match('Resource').where(f"_.uri='{uri}'").first()

    def get_node_attribute(self, system, entity, attribute):
        where_stmt = f"_.system=~'(?i){system}' AND _.entity=~'(?i){entity}' AND _.attribute=~'(?i){attribute}'"
        return NodeMatcher(self.graph).match('NodeAttribute').where(where_stmt).first()

    def get_harmonized_attribute(self, system, entity, attribute):
        where_stmt = f"_.system=~'(?i){system}' AND _.entity=~'(?i){entity}' AND _.attribute=~'(?i){attribute}'"
        return NodeMatcher(self.graph).match('HarmonizedAttribute').where(where_stmt).first()

    def assign_harmonized_attribute(self, node_attribute: NodeAttribute, harmonized_attribute: HarmonizedAttribute):
        """
        Assigns the relationship between a harmonized_attribute and a node_attribte
        :param node_attribute:
        :param harmonized_attribute:
        :return:
        """
        if len(node_attribute.harmonized_attribute) == 0:
            tx = self.graph.begin()
            na_node = self.get_resource_by_uri('NodeAttribute', node_attribute.uri)
            ha_node = self.get_resource_by_uri('HarmonizedAttribute', harmonized_attribute.uri)
            tx.create(Relationship(na_node, 'MAPS_TO', ha_node))
            tx.commit()

    def find_mappings_of_harmonized_attribute(self, system: str, entity: str, attribute: str, pagination: bool = False,
                                              page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> MappingSet:
        where_stmt = MdrGraph.build_where_statement_case_insensitive('c', system=system, entity=entity, attribute=attribute)
        skip_size = (page-1) * page_size
        paging_stmt = f' SKIP {skip_size} LIMIT {page_size} ' if pagination else ''
        return self.find_permissible_value_mappings(where_stmt, paging_stmt)

    def find_mappings_of_node_attribute(self, system: str, entity: str, attribute: str, pagination: bool = True,
                                      page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> MappingSet:
        where_stmt = MdrGraph.build_where_statement_case_insensitive('n', system=system, entity=entity, attribute=attribute)
        skip_size = (page-1) * page_size
        paging_stmt = f' SKIP {skip_size} LIMIT {page_size} ' if pagination else ''
        return self.find_permissible_value_mappings(where_stmt, paging_stmt)

    def find_mappings_of_concept_reference(self, curie: str) -> MappingSet:
        uri = curie_to_uri(curie)
        query = """        
        MATCH (c:HarmonizedAttribute)<-[:MAPS_TO]-(n:NodeAttribute)-[:USES]->(:Enumeration)
        -[:HAS_PERMISSIBLE_VALUE]->(p:PermissibleValue)<-[:MAPPED_FROM]-(m:Mapping)
        -[:MAPPED_TO]->(v:ConceptReference {uri: $uri})
        RETURN n.system + '.' + n.entity + '.' + n.attribute as subject_match_field,
        p.pref_label as subject_label,
        v.uri as object_id, v.designation as object_label,
        'CDM' + '.' + c.entity + '.' + c.attribute as object_match_field,
        m.predicate_id as predicate_id,
        m.creator_id as creator_id,
        m.comment as comment,
        m.mapping_date as mapping_date
        """
        cursor: Cursor = self.graph.run(query, uri=uri)
        mapping_set = MappingSet(mapping_provider=str(CCDH),
                                 creator_id='https://orcid.org/0000-0000-0000-0000',
                                 creator_label='CCDH',
                                 license='https://creativecommons.org/publicdomain/zero/1.0/')
        mappings = []
        while cursor.forward():
            current = dict(cursor.current)
            if current['object_id']:
                current['object_id'] = uri_to_curie(current['object_id'])
            if current['predicate_id']:
                current['predicate_id'] = uri_to_curie(current['predicate_id'])
            mappings.append(current)
        mapping_set.mappings = mappings
        return mapping_set


    def find_permissible_value_mappings(self, where_stmt, paging_stmt) -> MappingSet:
        where_stmt = 'WHERE ' + where_stmt if where_stmt else ''
        query = f"""        
        MATCH (c:HarmonizedAttribute)<-[:MAPS_TO]-(n:NodeAttribute)-[:USES]->(:Enumeration)
        -[:HAS_PERMISSIBLE_VALUE]->(p:PermissibleValue)
        {where_stmt}
        OPTIONAL MATCH (p)<-[:MAPPED_FROM]-(m:Mapping)-[:MAPPED_TO]->(v:ConceptReference)
        RETURN n.system + '.' + n.entity + '.' + n.attribute as subject_match_field,
        p.pref_label as subject_label,
        v.uri as object_id, v.designation as object_label,
        'CDM' + '.' + c.entity + '.' + c.attribute as object_match_field,
        m.predicate_id as predicate_id,
        m.creator_id as creator_id,
        m.comment as comment,
        m.mapping_date as mapping_date
        {paging_stmt}
        """
        query = query.format(where_stmt=where_stmt, pageing_stmt=paging_stmt)
        cursor: Cursor = self.graph.run(query)
        mapping_set = MappingSet(mapping_provider=str(CCDH),
                                 creator_id='https://orcid.org/0000-0000-0000-0000',
                                 creator_label='CCDH',
                                 license='https://creativecommons.org/publicdomain/zero/1.0/')
        mappings = []
        while cursor.forward():
            current = dict(cursor.current)
            if current['object_id']:
                current['object_id'] = uri_to_curie(current['object_id'])
            if current['predicate_id']:
                current['predicate_id'] = uri_to_curie(current['predicate_id'])
            mappings.append(current)
        mapping_set.mappings = mappings
        return mapping_set

    def find_permissible_values(self, value: str):
        query = f'''        
        MATCH (p:PermissibleValue)<-[:HAS_PERMISSIBLE_VALUE]-(:Enumeration)<-[:USES]-(d:NodeAttribute)
        WHERE p.pref_label=~'(?i){value}'
        OPTIONAL MATCH (v:ConceptReference)<-[:MAPPED_TO]-(m:Mapping)-[:MAPPED_FROM]->(p) 
        return p, d, v
        '''
        pvs = []
        cursor = self.graph.run(query)
        while cursor.forward():
            p, d, v = cursor.current
            p['node_attribute'] = f'{d["system"]}.{d["entity"]}.{d["attribute"]}'
            p['meaning'] = v
            pvs.append(p)
        return pvs

    def find_permissible_values_of(self, system: str, entity: str, attribute: str):
        where_stmt = MdrGraph.build_where_statement_case_insensitive('c', system=system, entity=entity,
                                                                     attribute=attribute)
        query = f'''
        MATCH (c:HarmonizedAttribute)<-[:MAPS_TO]-(n:NodeAttribute)-[:USES]->(:Enumeration)
        -[:HAS_PERMISSIBLE_VALUE]->(p:PermissibleValue)
        WHERE {where_stmt}
        RETURN DISTINCT p.pref_label as pref_label, apoc.coll.toSet(COLLECT(n)) as node_attributes
        '''
        ret = []
        cursor: Cursor = self.graph.run(query)
        while cursor.forward():
            ret.append(cursor.current)
        return ret

    def find_concept_references_and_permissible_values_of(self, system: str, entity: str, attribute: str):
        where_stmt = MdrGraph.build_where_statement_case_insensitive('c', system=system, entity=entity,
                                                                     attribute=attribute)
        query = f'''
        MATCH (c:HarmonizedAttribute)<-[:MAPS_TO]-(n:NodeAttribute)-[:USES]->(:Enumeration)
        -[:HAS_PERMISSIBLE_VALUE]->(p:PermissibleValue)
        WHERE {where_stmt} AND NOT (p)<-[:MAPPED_FROM]-(:Mapping)
        RETURN DISTINCT p.pref_label as pref_label, apoc.coll.toSet(COLLECT(n)) as node_attributes
        '''
        pvs = []
        cursor: Cursor = self.graph.run(query)
        while cursor.forward():
            pvs.append(cursor.current)
        crs = []
        query = f'''
        MATCH (c:HarmonizedAttribute)-[:HAS_MEANING]->(:CodeSet)-[:HAS_MEMBER]->(cr:ConceptReference)<-[:MAPPED_TO]
        -(:Mapping)-[:MAPPED_FROM]->(pv:PermissibleValue)
        WHERE {where_stmt}
        RETURN DISTINCT cr, apoc.coll.toSet(COLLECT(pv)) as pv
        '''
        cursor: Cursor = self.graph.run(query)
        while cursor.forward():
            crs.append(cursor.current)
        return crs, pvs

    def find_concept_reference(self, notation, defined_in, version=None):
        where_stmt = f"_.notation='{notation}' AND _.defined_in='{defined_in}'"
        if version:
            where_stmt += f" AND _.version='{version}'"
        return NodeMatcher(self.graph).match('ConceptReference').where(where_stmt).first()

    def find_concept_reference(self, uri):
        query = '''
        MATCH (v:ConceptReference {uri: $uri})
        OPTIONAL MATCH (v)<-[:MAPPED_TO]-(m:Mapping)-[:MAPPED_FROM]->(pv:PermissibleValue)<-[:HAS_PERMISSIBLE_VALUE]-(:Enumeration)<-[:USES]-(d:NodeAttribute)
        RETURN v, pv, d
        '''
        v = None
        pvs = []
        cursor: Cursor = self.graph.run(query, uri=uri)
        while cursor.forward():
            v, pv, d = cursor.current
            pv['node_attribute'] = d
            pvs.append(pv)
        if v is not None:
            v['representations'] = pvs
        return v

    def find_value_domain(self, permissible_values: List[str], system, entity, attribute) -> Union[str, None]:
        query = "MATCH (n:ValueDomain)<-[:USES]-(:NodeAttribute {system: $system, entity: $entity, attribute: $attribute})\n"
        for pv in permissible_values:
            query += f"MATCH (n:ValueDomain)-[:HAS_MEMBER]->(:PermissibleValue{{value: \"{pv}\"}})\n"
        query += f"MATCH (n)-[r:HAS_MEMBER]->(:PermissibleValue) WITH n, count(r) as pvcount\n"
        query += f"WHERE pvcount={len(permissible_values)}\n"
        query += "RETURN n"
        cursor: Cursor = self.graph.run(query, system=system, entity=entity, attribute=attribute)
        if cursor.forward():
            return cursor.current
        else:
            return None

    def find_harmonized_attributes(self, system, entity, attribute):
        where_stmt = MdrGraph.build_where_statement_case_insensitive('_', entity=entity, attribute=attribute)
        return NodeMatcher(self.graph).match('HarmonizedAttribute').where(where_stmt)

    def find_node_attributes(self, system, entity=None, attribute=None):
        where_stmt = MdrGraph.build_where_statement_case_insensitive('_', system=system, entity=entity, attribute=attribute)
        return NodeMatcher(self.graph).match('NodeAttribute').where(where_stmt)

    def find_node_attributes_complete(self, system, entity=None, attribute=None):
        where_stmt = MdrGraph.build_where_statement_case_insensitive('n', system=system, entity=entity, attribute=attribute)
        query = f'''
        MATCH (n:NodeAttribute)
        WHERE {where_stmt}
        OPTIONAL MATCH (d:HarmonizedAttribute)<-[:HAS_MEANING]-(n)
        OPTIONAL MATCH (n)-[:USES]->(:ValueDomain)-[:HAS_MEMBER]->(p:PermissibleValue)
        RETURN n, d, COLLECT(p.pref_label) as pvs
        '''
        cursor: Cursor = self.graph.run(query)
        records = []
        while cursor.forward():
            n, d, pvs = cursor.current
            n['harmonized_attribute'] = d
            n['permissible_values'] = pvs
            records.append(n)
        return records

    def find_harmonized_attributes_complete(self, system, entity, attribute):
        where_stmt = MdrGraph.build_where_statement_case_insensitive('n', system=system, entity=entity, attribute=attribute)
        query = f'''
        MATCH (n:HarmonizedAttribute)
        WHERE {where_stmt}
        OPTIONAL MATCH (c:ConceptReference)<-[:HAS_MEMBER]-(cd:CodeSet)<-[:HAS_MEANING]-(n)        
        OPTIONAL MATCH (n)<-[:MAPS_TO]-(d:NodeAttribute)
        RETURN n, apoc.coll.toSet(COLLECT(d)) as node_attributes, apoc.coll.toSet(COLLECT(c)) as concept_references     
        '''
        cursor: Cursor = self.graph.run(query)
        records = []
        while cursor.forward():
            dec, des, vms = cursor.current
            dec['node_attributes'] = des
            dec['concept_references'] = vms
            records.append(dec)
        return records
