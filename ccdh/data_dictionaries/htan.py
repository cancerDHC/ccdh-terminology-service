import csv
import re
import sys
from pathlib import Path

from ccdh.data_dictionaries.cdm import cdm_dictionary_sheet
from ccdh.data_dictionaries.gdc import expand_rows

HTAN_DIR = Path(__file__).parent.parent / 'crdc-nodes/HTAN-data-pipeline'
sys.path.append(str(HTAN_DIR))

from schematic.schemas.explorer import SchemaExplorer

PATH_TO_JSONLD = HTAN_DIR / 'data/schema_org_schemas/HTAN.jsonld'


def field_name(name: str) -> str:
    return name.replace('_', ' ').title().replace(' ', '')


def split_term(term: str) -> str:
    res_list = []
    res_list = re.findall('[A-Z][^A-Z]+', term)
    return ' '.join(res_list)


def htan_values(rows: iter):
    schema_explorer = SchemaExplorer()
    schema_explorer.load_schema(str(PATH_TO_JSONLD))
    new_rows = []
    for row in rows:
        node, entity, attr = row[0].split('.')
        if node != 'HTAN':
            new_rows.append(row)
            continue
        attr_name = field_name(attr)
        try:
            schema_explorer.is_class_in_schema(attr_name)
        except KeyError:
            print(f'HTAN | {attr} not found')
            continue

        codes = [split_term(term) for term in schema_explorer.find_children_classes(attr_name)]
        new_rows.extend(expand_rows(row, codes, ''))
    return new_rows


def main():
    rows = htan_values(cdm_dictionary_sheet('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4'))
    with open('htan.tsv', 'w', newline='') as f_output:
        tsv_output = csv.writer(f_output, delimiter='\t')
        for row in rows:
            tsv_output.writerow(row)


if __name__ == '__main__':
    main()
