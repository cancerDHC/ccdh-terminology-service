from dataclasses import dataclass
from py2neo.ogm import Model, Property, RelatedFrom, RelatedTo


@dataclass
class DataElement(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    context: str = Property()
    entity: str = Property()
    attribute: str = Property()

    value_domain = RelatedFrom('ValueDomain', 'DOMAIN_OF')
    data_element_concept = RelatedTo('DataElementConcept', 'REPRESENTS')


@dataclass
class ValueDomain(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    data_element = RelatedTo(DataElement, 'DOMAIN_OF')
    permissible_values = RelatedFrom('PermissibleValue', 'PART_OF')


@dataclass
class PermissibleValue(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    value: str = Property()
    value_domain = RelatedTo(ValueDomain, 'PART_OF')
    value_meaning = RelatedTo('ValueMeaning', 'MAPS_TO')


@dataclass
class ValueMeaning(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    code: str = Property()
    code_system: str = Property()
    display: str = Property()

    permissible_values = RelatedFrom(PermissibleValue, 'MAPS_TO')
    concept_domain = RelatedTo('ConceptualDomain', 'PART_OF')


@dataclass
class ConceptualDomain(Model):
    __primarykey__ = 'identifier'
    identifier: str = Property()
    name: str = Property()
    uri: str = Property()
    data_element_concept = RelatedTo('DataElementConcept', 'DOMAIN_OF')
    value_meanings = RelatedFrom(ValueMeaning, 'PART_OF')


@dataclass
class DataElementConcept(Model):
    __primarykey__ = 'identifier'
    name: str = Property()
    object_class: str = Property()
    property: str = Property()
    conceptual_domain = RelatedFrom(ConceptualDomain, 'DOMAIN_OF')
    data_element = RelatedFrom(DataElement, 'REPRESENTS')





