import sys
import uuid
from collections import namedtuple
from typing import List, Union, Tuple
from py2neo import Graph, Relationship, Node, NodeMatcher, Cursor, Subgraph
from py2neo.cypher import cypher_escape

from ccdh.mdr.models import *
from pathlib import Path
from urllib.parse import quote_plus
from sssom.sssom_datamodel import MappingSet, Mapping
from sssom.io import *
from ccdh.config import DEFAULT_PAGE_SIZE


class MdrGraph:
    def __init__(self, graph: Graph):
        self.graph = graph

    @staticmethod
    def create_data_element(context: str, entity: str, attr: str) -> Node:
        data_element = Node('DataElement',
                            identifier=f'http://ccdh/data_elements/{context}/{entity}/{attr}',
                            entity=entity, attribute=attr, context=context)
        return data_element

    @staticmethod
    def create_value_domain(permissible_values: List[str]) -> Tuple[Subgraph]:
        identifier = 'http://ccdh/value-domain/' + str(uuid.uuid4())
        value_domain = Node('ValueDomain', identifier=identifier)
        return value_domain

    @staticmethod
    def create_value_meaning(code, code_system, display, version=None):
        value_meaning = Node('ValueMeaning', code=code, code_system=code_system, display=display)
        if version is not None:
            value_meaning['version'] = version
        return value_meaning

    @staticmethod
    def create_permissible_value(value):
        pv = Node('PermissibleValue', value=value, identifier=str(uuid.uuid4()))
        return pv

    @staticmethod
    def create_data_element_concept(object_class, prop):
        return Node('DataElementConcept', object_class=object_class, property=prop)

    def get_node_by_identifier(self, node_type: str,  identifier: str) -> Node:
        return NodeMatcher(self.graph).match(node_type).where(f"_.identifier='{identifier}'").first()

    def get_data_element(self, context, entity, attribute):
        where_stmt = f"_.context='{context}' AND _.entity='{entity}' AND _.attribute='{attribute}'"
        return NodeMatcher(self.graph).match('DataElement').where(where_stmt).first()

    def assign_data_element_concept(self, data_element: DataElement, data_element_concept: DataElementConcept):
        if len(data_element.data_element_concept) == 1:
            return
        tx = self.graph.begin()
        de_node = self.get_node_by_identifier('DataElement', data_element.identifier)
        dec_node = self.get_node_by_identifier('DataElementConcept', data_element_concept.identifier)
        tx.create(Relationship(de_node, 'REPRESENTS', dec_node))
        tx.commit()

    def get_permissible_value_mapping(self, context: str, entity: str, attribute: str, pagination: bool = True,
                                      page: int = 1, page_size: int = DEFAULT_PAGE_SIZE) -> MappingSetDocument:
        where_list = []
        if context is not None:
            where_list.append(f"n.context='{context}'")
        if entity is not None:
            where_list.append(f"n.entity='{entity}'")
        if attribute is not None:
            where_list.append(f"n.attribute='{attribute}'")
        where_stmt = 'WHERE ' + ' AND '.join(where_list) if where_list else ''
        skip_size = (page-1) * page_size
        paging_stmt = f' SKIP {skip_size} LIMIT {page_size} ' if pagination else ''
        query = f"""        
        MATCH (c:DataElementConcept)<-[:REPRESENTS]-(n:DataElement)<-[:DOMAIN_OF]-(:ValueDomain)
        <-[:PART_OF]-(p:PermissibleValue)
        {where_stmt}
        OPTIONAL MATCH (p:PermissibleValue)<-[:MEANING_OF]-(v:ValueMeaning)
        RETURN n.context + '.' + n.entity + '.' + n.attribute as subject_match_context,
        p.value as subject_label, p.identifier as subject_id,
        v.code as object_id, v.display as object_label,
        'CDM' + '.' + c.object_class + '.' + c.property as object_match_context
        {paging_stmt}
        """
        query = query.format(where_stmt=where_stmt, pageing_stmt=paging_stmt)
        print(query)
        cursor: Cursor = self.graph.run(query)
        mapping_set = MappingSet(mapping_provider='http://ccdh',
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
        df = cursor.to_data_frame()
        curie_map = {
            'NCIT': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#'
        }
        mapping_set_doc: MappingSetDocument = MappingSetDocument(mapping_set, curie_map)
        return mapping_set_doc

    def find_value_meaning(self, code, code_system, version=None):
        where_stmt = f"_.code='{code}' AND _.code_system='{code_system}'"
        if version:
            where_stmt += f" AND _.version='{version}'"
        return NodeMatcher(self.graph).match('ValueMeaning').where(where_stmt).first()

    def find_value_domain(self, permissible_values: List[str]) -> Union[str, None]:
        query = ''
        for pv in permissible_values:
            query += f"MATCH (n:ValueDomain)<-[:PART_OF]-(:PermissibleValue{{value: '{pv}'}})\n"
        query += f"MATCH (n)<-[r:PART_OF]-(:PermissibleValue)\n"
        query += f"WHERE count(r)={len(permissible_values)}\n"
        query += "RETURN n"
        cursor: Cursor = self.graph.run(query)
        if cursor.forward():
            return cursor.current
        else:
            return None

    def find_data_element_concept(self, object_class, prop):
        where_stmt = f"_.object_class='{object_class}' AND _.property='{prop}'"
        return NodeMatcher(self.graph).match('DataElementConcept').where(where_stmt).first()

