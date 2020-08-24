from biolinkml.meta import SchemaDefinition, SlotDefinition, ElementName, ClassDefinition
from typing import List
from ccdh.cdm import class_definition

from biolinkml.utils.yamlutils import extended_str, as_yaml


class TabularSchemaDefinitionLoader(object):
    def __init__(self):
        ...

    @classmethod
    def load(cls, name, rows: List[List]) -> SchemaDefinition:
        schema: SchemaDefinition = SchemaDefinition(name=name, id='https://ccdh.org/model/specimen')
        klass: ClassDefinition = ClassDefinition(name=name)
        schema.classes = {name: klass}
        schema.license = 'https://creativecommons.org/publicdomain/zero/1.0/'
        schema.description = rows[1][5]
        schema.notes.append(rows[3][5])
        schema.mappings.extend([i.strip() for i in rows[2][5].split('\n')])
        for row in rows[5:]:
            if row[0] == 'DEPRECATED/EXPLORATORY ATTRIBUTES':
                break
            slot: SlotDefinition = TabularSchemaDefinitionLoader.load_slot(row)
            klass.slot_usage[slot.name] = slot
        return schema

    @classmethod
    def load_slot(cls, row: List) -> SlotDefinition:
        slot: SlotDefinition = SlotDefinition(name=row[5])
        slot.description = row[6]
        slot.mappings = []
        slot.mappings.extend(['ADM:' + i.strip() for i in row[11].split('\n') if i.strip()])
        slot.mappings.extend([i.strip().replace('.', ':', 1) for i in row[12].split('\n')])
        slot.mappings.extend(['FHIR:' + i.strip() for i in row[13].split('\n')])
        slot.range = ElementName(row[7])
        slot = TabularSchemaDefinitionLoader.cardinality_to_slot(slot, row[8])
        slot.comments.extend(filter(lambda a: len(a.strip()) > 0, row[9].split('\n')))
        return slot

    @classmethod
    def cardinality_to_slot(cls, slot, card):
        if card == '0..1':
            slot.required = False
            slot.multivalued = False
        elif card == '0..m':
            slot.required = False
            slot.multivalued = True
        return slot


def load_ccdh_specimen():
    rows: List[List] = class_definition('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4', 'Specimen')
    schema: SchemaDefinition = TabularSchemaDefinitionLoader.load('Specimen', rows)
    print(as_yaml(schema))


if __name__ == '__main__':
    load_ccdh_specimen()
