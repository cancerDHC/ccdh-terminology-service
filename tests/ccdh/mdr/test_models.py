import pytest
from py2neo import NodeMatcher

from ccdh.mdr.models import *


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
    value_domain = ValueDomain(identifier='vd_1')

    tx = neo4j_graph.begin()
    tx.create(value_domain)
    tx.commit()

    yield value_domain
    tx = neo4j_graph.begin()
    tx.delete(value_domain)
    tx.finish()


def test_value_domain(neo4j_graph, value_domain):
    node = NodeMatcher(neo4j_graph).match('ValueDomain').first()
    assert node is not None


def test_assign_data_element(neo4j_graph, value_domain):
    tx = neo4j_graph.begin()
    data_element = DataElement(identifier='de_1', title='GDC Sample Tissue',
                               context='GDC', entity='sample', attribute='tissue_type')
    data_element.value_domain.add(value_domain)
    tx.merge(data_element)
    tx.commit()

    de: DataElement = DataElement.match(neo4j_graph).where("_.identifier='de_1'").first()
    assert len(de.value_domain) == 1

    vd: ValueDomain = ValueDomain.match(neo4j_graph).where("_.identifier='vd_1'").first()
    assert len(vd.data_element) == 1


def test_value_meaning_dataclass():
    vm = ValueMeaning(identifier='vm_1', code='12345', code_system='ncit', display='test')
    pm = PermissibleValue(identifier='pm_1', value='my test')
    vm.permissible_values.add(pm)
    assert vm.display == 'test'
    assert vm.code == '12345'
    assert len(vm.permissible_values) == 1


