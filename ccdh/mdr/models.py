from py2neo.ogm import Model, Property, RelatedFrom, RelatedTo


class DataElement(Model):
    __primarykey__ = 'identifier'
    identifier = Property()
    title = Property()
    context = Property()
    entity = Property()
    attribute = Property()

    value_domain = RelatedFrom('ValueDomain', 'DOMAIN_OF')
    data_element_concept = RelatedTo('DataElementConcept', 'REPRESENTS')


class ValueDomain(Model):
    __primarykey__ = 'identifier'
    identifier = Property()
    data_element = RelatedTo(DataElement)


class EnumeratedValueDomain(ValueDomain):
    __primarykey__ = 'identifier'
    identifier = Property()
    permissible_values = RelatedFrom('PermissibleValue', 'PART_OF')


class PermissibleValue(Model):
    __primarykey__ = 'identifier'
    identifier = Property()
    value_domain = RelatedTo(EnumeratedValueDomain)
    value_meaning = RelatedTo('ValueMeaning', 'MAPS_TO')


class ValueMeaning(Model):
    __primarykey__ = 'identifier'
    identifier = Property()
    code = Property()
    code_system = Property()
    label = Property()

    permissible_value = RelatedFrom(PermissibleValue)
    concept_domain = RelatedTo('ConceptualDomain', 'PART_OF')


class ConceptualDomain(Model):
    __primarykey__ = 'identifier'
    identifier = Property()
    name = Property()
    data_element_concept = RelatedTo('DataElementConcept', 'DOMAIN_OF')


class EnumeratedConceptualDomain(ConceptualDomain):
    __primarykey__ = 'identifier'
    name = Property()
    value_meanings = RelatedFrom(ValueMeaning)
    uri = Property()


class DataElementConcept(Model):
    __primarykey__ = 'identifier'
    name = Property()
    object_class = Property()
    property = Property()
    sconceptual_domain = RelatedFrom(ConceptualDomain)
    data_element = RelatedFrom(DataElement, 'REPRESENTS')





