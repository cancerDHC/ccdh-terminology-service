from sssom.sssom_datamodel import Mapping, MappingSet
import pytest
from ccdh.namespaces import NAMESPACES


@pytest.fixture
def curie_map() -> dict:
    curie_map = {
        'EX': 'http://example.org/',
    }


def test_mapping_set():
    curie_map = NAMESPACES
    mapping_set = MappingSet()
    mapping = Mapping()
    mapping.subject_id = 'EX:s1'
    mapping.object_id = 'EX:o1'
    mapping.comment = 'a mapping example'
    mapping.mapping_provider = 'ccdh'
    mapping_set.curie_map = curie_map
    mapping_set.mappings.append(mapping)