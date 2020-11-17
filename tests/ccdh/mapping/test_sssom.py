from sssom.sssom_datamodel import *
from sssom.io import *
import pytest
# Some tests to demonstrate how to use sssom-py

@pytest.fixture
def curie_map() -> dict:
    curie_map = {
        'EX': 'http://example.org/',
    }


def test_mapping_set(curie_map):
    mapping_set = MappingSet()
    mapping = Mapping()
    mapping.subject_id = 'EX:s1'
    mapping.object_id = 'EX:o1'
    mapping.comment = 'a mapping example'
    mapping.mapping_provider = 'ccdh'
    mapping_set_doc = MappingSetDocument(mapping_set, curie_map)
    print(to_tsv)