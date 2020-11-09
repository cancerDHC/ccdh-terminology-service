from ccdh.gdc import gdc_values
from ccdh.cdm import cdm_dictionary_sheet
from ccdh.mdr.importer import GdcImporter
from ccdh.config import neo4j_graph, ROOT_DIR
from typing import List
import csv


def read_mvp_tsv() -> List[str]:
    rows = list()
    with open(ROOT_DIR / 'output/CDA_MVP_V0_value_sets-20-10-22.tsv', 'r') as tsvfile:
        reader = csv.reader(tsvfile, delimiter='\t')
        next(reader)
        for row in reader:
            rows.append(row)
    return rows


def import_mvp():
    #rows = gdc_values(cdm_dictionary_sheet('1oWS7cao-fgz2MKWtyr8h2dEL9unX__0bJrWKv6mQmM4'))
    rows = read_mvp_tsv()
    tuples = list()
    importer = GdcImporter(neo4j_graph())
    for row in rows:
        context, entity, attribute = row[0].split('.')
        tuples.append((entity, attribute))
    tuples = set(tuples)
    for (entity, attribute) in tuples:
        importer.add_data_element(entity, attribute)


if __name__ == '__main__':
    import_mvp()