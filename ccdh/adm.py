from googleapiclient.discovery import build
from ccdh.gdrive.authorize import authorize
from typing import Dict
import pprint

pp = pprint.PrettyPrinter()

def adm(sheet_id: str, range: str) -> Dict:
    """
    Extract ADM models from Google Drive
    :param str sheet_id: The identifier of the google sheet

    :return: A list of adm values
    """
    nodes = {}

    service = build('sheets', 'v4', credentials=authorize())

    # Call the Sheets API
    result = service.spreadsheets().values().batchGet(spreadsheetId=sheet_id, ranges='Dictionary').execute()
    value_ranges = result.get('valueRanges', [])
    for values in value_ranges[0]['values']:
        if len(values) < 6:
            continue
        node_entity, prop = map(str.strip, values[4:6])
        if node_entity and prop and '.' in node_entity:
            node, entity = map(str.strip, node_entity.split('.'))
            add_entity_property(nodes, node, entity, prop)

    return nodes


def add_entity_property(nodes: Dict, node: str, entity: str, prop: str) -> Dict:
    """
    Add an ADM property
    :param nodes:
    :param node:
    :param entity:
    :param prop:
    :return:
    """
    node_entities = nodes.get(node, {})
    entity_props = node_entities.get(entity, set())
    entity_props.add(prop)
    node_entities[entity] = entity_props
    nodes[node] = node_entities
    return nodes


def main():
    nodes = adm('1AbKbWZuUSZ_pzP5VgQHptgS8o_8bMyrmhmoOksKDBBE', 'Dictionary')
    pp.pprint(nodes)


if __name__ == '__main__':
    main()
