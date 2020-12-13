from typing import List, Union, Tuple
from urllib.parse import quote_plus

import shortuuid
from py2neo import Relationship, Node, NodeMatcher, Cursor, Subgraph, Graph
from sssom.io import *
from prefixcommons import expand_uri, contract_uri

# from ccdh.config import DEFAULT_PAGE_SIZE
from ccdh.mdr.models import *

from ccdh.namespaces import CCDH, GDC, PDC, NAMESPACES

DEFAULT_PAGE_SIZE = 25

class MdrGraph:
    def __init__(self, graph: Graph):
        self.graph = graph

    @staticmethod
    def create_data_element_uri(context: str, entity: str, attr: str) -> str:
        return str(CCDH[f'data-element/{quote_plus(context)}/{quote_plus(entity)}/{quote_plus(attr)}'])

    @staticmethod
    def create_value_domain_uri():
        return str(CCDH[f'value-domain/{shortuuid.uuid()}'])

    @staticmethod
    def create_data_element_concept_uri(context, object_class, prop):
        return str(CCDH[f'data-element-concept/{quote_plus(context)}/{quote_plus(object_class)}/{quote_plus(prop)}'])

    @staticmethod
    def create_permissible_value_uri():
        return str(CCDH[f'permissible-values/{shortuuid.uuid()}'])

    @staticmethod
    def create_conceptual_domain_uri():
        return str(CCDH[f'conceptual-domain/{shortuuid.uuid()}'])

    @staticmethod
    def create_conceptual_domain() -> Node:
        uri = MdrGraph.create_conceptual_domain_uri()
        return Node('ConceptualDomain', 'Resource', 'CodeSet', uri=uri)

    @staticmethod
    def create_data_element(context: str, entity: str, attr: str) -> Node:
        uri = MdrGraph.create_data_element_uri(context, entity, attr)
        return Node('DataElement', 'Resource', uri=uri, entity=entity, attribute=attr, context=context)

    @staticmethod
    def create_value_domain() -> Tuple[Subgraph]:
        uri = MdrGraph.create_value_domain_uri()
        return Node('ValueDomain', 'Resource', 'CodeSet', uri=uri)

    @staticmethod
    def create_value_meaning(uri, notation, scheme, pref_label, version=None, is_curie=True):
        uri = expand_uri(uri, NAMESPACES) if is_curie else uri
        value_meaning = Node('ValueMeaning', 'Resource', uri=uri, notation=notation, inScheme=scheme,
                             prefLabel=pref_label, version=version)
        return value_meaning

    @staticmethod
    def create_permissible_value(value: str):
        uri = MdrGraph.create_permissible_value_uri()
        pv = Node('PermissibleValue', 'Resource', prefLabel=value, uri=uri)
        return pv

    @staticmethod
    def create_data_element_concept(context, objectClass: str, prop: str):
        uri = MdrGraph.create_data_element_concept_uri(context, objectClass, prop)
        return Node('DataElementConcept', 'Resource', uri=uri, context=context, objectClass=objectClass, property=prop)

    @staticmethod
    def build_where_statement(node_str, **kwargs):
        where_list = [f"{node_str}.{key}='{kwargs[key]}'" for key in kwargs if kwargs[key] is not None]
        return ' AND '.join(where_list)

    def get_resource_by_uri(self, uri: str) -> Node:
        return NodeMatcher(self.graph).match('Resource').where(f"_.uri='{uri}'").first()

    def get_data_element(self, context, entity, attribute):
        where_stmt = f"_.context='{context}' AND _.entity='{entity}' AND _.attribute='{attribute}'"
        return NodeMatcher(self.graph).match('DataElement').where(where_stmt).first()

    def get_data_element_concept(self, context, objectClass, property):
        where_stmt = f"_.context='{context}' AND _.objectClass='{objectClass}' AND _.property='{property}'"
        return NodeMatcher(self.graph).match('DataElementConcept').where(where_stmt).first()

    def assign_data_element_concept(self, data_element: DataElement, data_element_concept: DataElementConcept):
        if len(data_element.data_element_concept) == 1:
            return
        tx = self.graph.begin()
        de_node = self.get_resource_by_uri('DataElement', data_element.uri)
        dec_node = self.get_resource_by_uri('DataElementConcept', data_element_concept.uri)
        tx.create(Relationship(dec_node, 'HAS_REPRESENTATION', de_node))
        tx.commit()

    def find_mappings_of_data_element_concept(self, object_class: str, property: str, pagination: bool = False,
                                              page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> MappingSet:
        where_stmt = MdrGraph.build_where_statement('c', objectClass=object_class, property=property)
        skip_size = (page-1) * page_size
        paging_stmt = f' SKIP {skip_size} LIMIT {page_size} ' if pagination else ''
        return self.find_permissible_value_mappings(where_stmt, paging_stmt)

    def find_mappings_of_data_element(self, context: str, entity: str, attribute: str, pagination: bool = True,
                                      page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> MappingSet:
        where_stmt = MdrGraph.build_where_statement('n', context=context, entity=entity, attribute=attribute)
        skip_size = (page-1) * page_size
        paging_stmt = f' SKIP {skip_size} LIMIT {page_size} ' if pagination else ''
        return self.find_permissible_value_mappings(where_stmt, paging_stmt)

    def find_permissible_value_mappings(self, where_stmt, paging_stmt) -> MappingSet:
        where_stmt = 'WHERE ' + where_stmt if where_stmt else ''
        query = f"""        
        MATCH (c:DataElementConcept)<-[:HAS_MEANING]-(n:DataElement)-[:USES]->(:ValueDomain)
        -[:HAS_MEMBER]->(p:PermissibleValue)
        {where_stmt}
        OPTIONAL MATCH (p:PermissibleValue)<-[r:HAS_REPRESENTATION]-(v:ValueMeaning)
        RETURN n.context + '.' + n.entity + '.' + n.attribute as subject_match_field,
        p.prefLabel as subject_label, p.uri as subject_id,
        v.uri as object_id, v.prefLabel as object_label,
        'CDM' + '.' + c.objectClass + '.' + c.property as object_match_field,
        r.predicate_id as predicate_id,
        r.creator_id as creator_id,
        r.comment as comment,
        r.mapping_date as mapping_date
        {paging_stmt}
        """
        query = query.format(where_stmt=where_stmt, pageing_stmt=paging_stmt)
        print(query)
        cursor: Cursor = self.graph.run(query)
        mapping_set = MappingSet(mapping_provider=str(CCDH),
                                 creator_id='https://orcid.org/0000-0000-0000-0000',
                                 creator_label='CCDH',
                                 license='https://creativecommons.org/publicdomain/zero/1.0/')
        mappings = []
        while cursor.forward():
            current = cursor.current
            mapping = Mapping()
            for key in current.keys():
                mapping[key] = current[key]
            mappings.append(mapping)
        mapping_set.mappings = mappings
        return mapping_set

    def find_value_meaning(self, notation, scheme, version=None):
        where_stmt = f"_.notation='{notation}' AND _.inScheme='{scheme}'"
        if version:
            where_stmt += f" AND _.version='{version}'"
        return NodeMatcher(self.graph).match('ValueMeaning').where(where_stmt).first()

    def find_value_domain(self, permissible_values: List[str], context, entity, attribute) -> Union[str, None]:
        query = "MATCH (n:ValueDomain)<-[:USES]-(:DataElement {context: $context, entity: $entity, attribute: $attribute})\n"
        for pv in permissible_values:
            query += f"MATCH (n:ValueDomain)-[:HAS_MEMBER]->(:PermissibleValue{{value: \"{pv}\"}})\n"
        query += f"MATCH (n)-[r:HAS_MEMBER]->(:PermissibleValue) WITH n, count(r) as pvcount\n"
        query += f"WHERE pvcount={len(permissible_values)}\n"
        query += "RETURN n"
        cursor: Cursor = self.graph.run(query, context=context, entity=entity, attribute=attribute)
        if cursor.forward():
            return cursor.current
        else:
            return None

    def find_data_element_concepts(self, context, objectClass, prop):
        where_stmt = MdrGraph.build_where_statement('_', objectClass=objectClass, property=prop)
        return NodeMatcher(self.graph).match('DataElementConcept').where(where_stmt)

    def find_data_elements(self, context, entity=None, attribute=None):
        where_stmt = MdrGraph.build_where_statement('_', context=context, entity=entity, attribute=attribute)
        return NodeMatcher(self.graph).match('DataElement').where(where_stmt)



