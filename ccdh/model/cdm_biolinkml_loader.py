from biolinkml.meta import SchemaDefinition, SlotDefinition, ElementName, ClassDefinition, ClassDefinitionName
from typing import List
from ccdh.cdm import class_definition
import re

from biolinkml.utils.yamlutils import extended_str, as_yaml


class TabularSchemaDefinitionLoader(object):
    def __init__(self):
        ...

    @classmethod
    def load(cls, name, rows: List[List]) -> SchemaDefinition:
        schema: SchemaDefinition = SchemaDefinition(name=name, id='https://ccdh.org/model/specimen', title=name)
        klass: ClassDefinition = ClassDefinition(name=name, is_a=ClassDefinitionName('Entity'))
        schema.classes = {name: klass}
        schema.license = 'https://creativecommons.org/publicdomain/zero/1.0/'
        schema.prefixes = {
            'biolinkml': 'https://w3id.org/biolink/biolinkml/',
            'specimen': 'https://ccdh.org/specimen/'
        }
        schema.default_prefix = 'specimen'
        schema.imports = ['prefixes', 'entities', 'datatypes']
        schema.description = rows[1][5]
        schema.comments = rows[3][5].split('\n')
        schema.notes.append('derived from [CDM_Dictionary_v1](https://docs.google.com/spreadsheets/d/1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4/)')
        schema.mappings.extend([i.strip() for i in rows[2][5].split('\n')])
        deprecated = False
        for row in rows[5:]:
            # todo: use the deprecated slot
            # for exploratory attrs use subset
            if row[0] == 'DEPRECATED/EXPLORATORY ATTRIBUTES':
                deprecated = True
                continue
            slot: SlotDefinition = TabularSchemaDefinitionLoader.load_slot(row)
            if deprecated:
                slot.deprecated = True
            klass.slot_usage[slot.name] = slot
        return schema

    @classmethod
    def load_slot(cls, row: List) -> SlotDefinition:
        slot: SlotDefinition = SlotDefinition(name=row[5])
        slot.description = row[6]
        mappings = []
        mappings.extend(['ADM:' + i.strip() for i in row[11].split('\n') if i.strip()])
        mappings.extend([i.strip().replace('.', ':', 1) for i in row[12].split('\n') if i.strip()])
        mappings.extend(['FHIR:' + i.strip() for i in row[13].split('\n') if i.strip()])
        slot.mappings = list(filter(lambda x: re.match(r'^\w+:[\w\-\_]+\.[\w\-\_]+$', x), mappings))
        range_str = ElementName(row[7]).replace('*', '')
        range_str = re.sub(r'\([^)]*\)', '', range_str).strip()
        if '|' in range_str:
            range_str = 'Or'.join([i.strip() for i in range_str.split('|')])
        slot.range = range_str
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
        if slot.name == 'id':
            slot.required = True
        return slot


def load_ccdh_specimen() -> str:
    rows: List[List] = class_definition('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4', 'Specimen')
    schema: SchemaDefinition = TabularSchemaDefinitionLoader.load('Specimen', rows)
    yaml = as_yaml(schema)
    return '\n'.join([i for i in yaml.split('\n') if not re.match(r'^\s+name:.*', i)])


if __name__ == '__main__':
    print(load_ccdh_specimen())
