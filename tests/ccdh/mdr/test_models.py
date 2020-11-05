import pytest
from py2neo import NodeMatcher

from ccdh.mdr.models import DataElement, ValueDomain, EnumeratedValueDomain


@pytest.fixture
def data_element(neo4j_graph):
    data_element = DataElement()
    data_element.identifier = 'http://gdc/sample/tissue_type'
    data_element.context = 'gdc'
    data_element.entity = 'sample'
    data_element.attribute = 'tissue_type'

    tx = neo4j_graph.begin()
    tx.create(data_element)
    tx.commit()

    yield data_element
    tx.delete(data_element)
    tx.finish()


@pytest.fixture
def value_domain(neo4j_graph):
    value_domain = EnumeratedValueDomain()
    value_domain.identifier = 'http://value_domain/sample'

    tx = neo4j_graph.begin()
    tx.create(value_domain)
    tx.commit()

    yield value_domain
    tx.delete(value_domain)
    tx.finish()


def test_enumerated_value_domain(neo4j_graph, value_domain):
    node = NodeMatcher(neo4j_graph).match('EnumeratedValueDomain').first()
    assert node is not None
