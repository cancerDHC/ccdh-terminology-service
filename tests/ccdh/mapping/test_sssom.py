from sssom.sssom_datamodel import Mapping, MappingSet
from sssom.io import *
import pytest
from ccdh.api.routers.mappings import generate_sssom_tsv
from ccdh.namespaces import NAMESPACES
# Some tests to demonstrate how to use sssom-py


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