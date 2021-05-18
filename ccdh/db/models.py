from dataclasses import dataclass

import neotime
from py2neo.ogm import Model, Property, RelatedFrom, RelatedTo
from tccm_api.db.models import ConceptReference


@dataclass
class NodeAttribute(Model):
    # DataElement
    __primarykey__ = 'identifier'
    identifier: str = Property()
    system: str = Property()
    entity: str = Property()
    attribute: str = Property()
    version = Property(default=None)

    enumeration = RelatedTo("Enumeration", 'USES')
    harmonized_attribute = RelatedTo('HarmonizedAttribute', 'MAPS_TO')


@dataclass
class Enumeration(Model):
    # ValueDomain
    __primarykey__ = 'identifier'
    identifier: str = Property()
    node_attribute = RelatedFrom(NodeAttribute, 'USES')
    permissible_values = RelatedTo('PermissibleValue', 'HAS_PERMISSIBLE_VALUE')


@dataclass
class PermissibleValue(Model):
    # Permissible Value
    __primarykey__ = 'identifier'
    identifier: str = Property()
    value: str = Property()
    enumerated_value = RelatedFrom(Enumeration, 'HAS_PERMISSIBLE_VALUE')
    mappings = RelatedFrom('Mapping', 'MAPPED_FROM')


from dataclasses import dataclass
from py2neo.ogm import Model, Property, RelatedFrom, RelatedTo
from typing import List


@dataclass
class ConceptSystem(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    uri: str = Property()
    description: str = Property()
    prefix: str = Property()
    reference: List[str] = Property()
    namespace: str = Property()

    root_concept = RelatedTo(ConceptReference, 'ROOT_CONCEPT')


@dataclass
class CodeSet(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    description: str = Property()
    uri: str = Property()

    members = RelatedTo(ConceptReference, 'HAS_MEMBER')


# @dataclass
# class ConceptReference(Model):
#     __primarykey__ = 'identifier'
#     identifier: str = Property()
#     code: str = Property()
#     code_system: str = Property()
#     display: str = Property()
#
#     mappings = RelatedFrom('Mapping', 'MAPPED_TO')
#     code_sets = RelatedFrom('CodeSet', 'HAS_MEMBER')


@dataclass
class Mapping(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    match_type: str = Property()
    comment: str = Property()
    mapping_date: neotime.Date = Property()
    mapping_provider: str = Property()

    permissible_value = RelatedTo(PermissibleValue, 'MAPPED_FROM')
    concept_reference = RelatedTo(ConceptReference, 'MAPPED_TO')


@dataclass
class CodeSet(Model):
    # ConceptualDomain
    __primarykey__ = 'identifier'
    identifier: str = Property()
    name: str = Property()
    uri: str = Property()
    harmonized_attribute = RelatedFrom('HarmonizedAttribute', 'HAS_MEANING')
    concept_references = RelatedTo(ConceptReference, 'HAS_MEMBER')


@dataclass
class HarmonizedAttribute(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    system: str = Property()
    entity: str = Property()
    attribute: str = Property()
    version: str = Property(default=None)
    code_set = RelatedTo(CodeSet, 'HAS_MEANING')
    node_attributes = RelatedFrom(NodeAttribute, 'MAPS_TO')





