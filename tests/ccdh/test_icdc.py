import pytest
from ccdh.icdc import ICDCDictionary, ICDC_ROOT


@pytest.fixture
def icdc_dictionary():
    return ICDCDictionary(root_dir=ICDC_ROOT)


def test_read_icdc(icdc_dictionary):
    assert 'general_sample_pathology' in icdc_dictionary.properties
    assert 'sample' in icdc_dictionary.entities
