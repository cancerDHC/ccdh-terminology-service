from dataclasses import dataclass
from py2neo.ogm import Model, Property, RelatedFrom, RelatedTo


@dataclass
class DataElement(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    title: str = Property()
    context: str = Property()
    entity: str = Property()
    attribute: str = Property()

    value_domain = RelatedFrom('ValueDomain', 'DOMAIN_OF')
    data_element_concept = RelatedTo('DataElementConcept', 'REPRESENTS')


@dataclass
class ValueDomain(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    data_element = RelatedTo(DataElement)


@dataclass
class EnumeratedValueDomain(ValueDomain):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    permissible_values = RelatedFrom('PermissibleValue', 'PART_OF')


@dataclass
class PermissibleValue(Model):
    __primarykey__ = 'identifier'
    __primarylabel__ = 'value'
    identifier: str = Property()
    value: str = Property()
    value_domain = RelatedTo(EnumeratedValueDomain)
    value_meaning = RelatedTo('ValueMeaning', 'MAPS_TO')


@dataclass
class ValueMeaning(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    code: str = Property()
    code_system: str = Property()
    display: str = Property()

    permissible_values = RelatedFrom(PermissibleValue)
    concept_domain = RelatedTo('ConceptualDomain', 'PART_OF')


@dataclass
class ConceptualDomain(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    name: str = Property()
    data_element_concept = RelatedTo('DataElementConcept', 'DOMAIN_OF')


@dataclass
class EnumeratedConceptualDomain(ConceptualDomain):
    __primarykey__ = 'identifier'
    name: str = Property()
    value_meanings = RelatedFrom(ValueMeaning)
    uri: str = Property()


@dataclass
class DataElementConcept(Model):
    __primarykey__ = 'identifier'
    name: str = Property()
    object_class: str = Property()
    property: str = Property()
    sconceptual_domain = RelatedFrom(ConceptualDomain)
    data_element = RelatedFrom(DataElement, 'REPRESENTS')





