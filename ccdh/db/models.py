from dataclasses import dataclass

import neotime
from py2neo.ogm import Model, Property, RelatedFrom, RelatedTo


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
    permissible_values = RelatedFrom('PermissibleValue', 'PART_OF')


@dataclass
class PermissibleValue(Model):
    # Permissible Value
    __primarykey__ = 'identifier'
    identifier: str = Property()
    value: str = Property()
    enumerated_value = RelatedTo(Enumeration, 'PART_OF')
    mappings = RelatedFrom('Mapping', 'MAPPED_FROM')


@dataclass
class ConceptReference(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    code: str = Property()
    code_system: str = Property()
    display: str = Property()

    mappings = RelatedFrom('Mapping', 'MAPPED_TO')
    code_sets = RelatedFrom('CodeSet', 'HAS_MEMBER')


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
    harmonized_attribute = RelatedFrom('HarmanizedAttribute', 'HAS_MEANING')
    concept_references = RelatedTo(ConceptReference, 'HAS_MEMBER')


@dataclass
class HarmanizedAttribute(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    system: str = Property()
    entity: str = Property()
    attribute: str = Property()
    version: str = Property(default=None)
    code_set = RelatedTo(CodeSet, 'HAS_MEANING')
    node_attributes = RelatedFrom(NodeAttribute, 'MAPS_TO')





