from collections import namedtuple

from pathlib import Path
import csv
from typing import List
import sys

GDC_DIR = Path(__file__).parent.parent.parent / 'crdc-nodes/gdcdictionary'
print(GDC_DIR)
sys.path.append(str(GDC_DIR))

from gdcdictionary.python import GDCDictionary


MOD_DIR = GDC_DIR / 'gdcdictionary'
MAP_DIR = Path(__file__).parent.parent.parent / 'data/mappings/gdc-ncit'

ResolverPair = namedtuple('ResolverPair', ['resolver', 'source'])


def gdc_ncit_mappings():
    gdc_ncit_map = {}
    gdc_ncit_file = MAP_DIR / 'current.csv'
    with open(gdc_ncit_file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            target_code = row[3]
            if target_code not in gdc_ncit_map:
                gdc_ncit_map[target_code] = {}
            gdc_ncit_map[target_code][row[4]] = row
    return gdc_ncit_map


def expand_rows(row: List, codes: iter, cde_id) -> iter:
    gdc_ncit_map = gdc_ncit_mappings()
    new_rows = []
    for code in codes:
        new_row = [''] * 7
        new_row[0] = row[0]
        new_row[1] = code
        map_row = gdc_ncit_map.get(row[0].split('.')[-1], {}).get(code, [])
        new_row[3] = row[3]
        if map_row:
            new_row[2] = 'skos:exactMatch'
            new_row[4] = f'NCIT:{map_row[0]}'
            new_row[5] = map_row[1]
        if cde_id:
            new_row[6] = f'CDE:{str(cde_id)}'
        new_rows.append(new_row)
    return new_rows


def gdc_values(rows):
    gdc = GDCDictionary()
    new_rows = []
    for row in rows:
        node, entity, attr = row[0].split('.')
        yaml_file = f'{entity.lower()}.yaml'
        value_found = True
        if node.upper() != 'GDC':
            value_found = False
        elif yaml_file not in gdc.resolvers:
            print(f'GDC | {yaml_file} not found')
            value_found = False
        else:
            props = gdc.resolvers[yaml_file].source.get('properties', {})
            if attr not in props:
                print(f'GDC | {entity} | {attr} not found')
                value_found = False
        if not value_found:
            new_rows.append(row)
        else:
            cde_id = props[attr].get('termDef', {}).get('cde_id', '') or ''
            codes = props[attr].get('enum', [])
            new_rows.extend(expand_rows(row, codes, cde_id))
    return new_rows

