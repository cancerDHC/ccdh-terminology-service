import pytest
from py2neo import NodeMatcher

from ccdh.mdr.importer import GdcImporter


@pytest.fixture
def gdc_importer(neo4j_graph):
    gdc_importer = GdcImporter(neo4j_graph)
    return gdc_importer


def test_add_data_element(gdc_importer, neo4j_graph):
    gdc_importer.add_data_element('Aliquot', 'analyte_type')
    node = NodeMatcher(neo4j_graph).match('DataElement').first()
    assert node is not None

    node = NodeMatcher(neo4j_graph).match('ValueDomain').first()
    assert node is not None

    node = NodeMatcher(neo4j_graph).match('ValueMeaning').first()
    assert node is not None
    assert node['code_system'] == 'NCIT'


def test_assign_data_element_concept(gdc_importer, neo4j_graph):
    pass

