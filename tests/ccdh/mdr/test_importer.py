import pytest

from ccdh.mdr.gdc_data_dictionary_importer import GdcDataDictionaryImporter


@pytest.fixture
def gdc_importer(neo4j_graph):
    gdc_importer = GdcDataDictionaryImporter(neo4j_graph)
    return gdc_importer


def test_gdc_dictionary(gdc_dictionary):
    print('test')