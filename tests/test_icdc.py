import pytest
from ccdh.icdc import ICDCDictionary, ICDC_ROOT


@pytest.fixture
def icdc_dictionary():
    return ICDCDictionary(root_dir=ICDC_ROOT)


def test_read_icdc(icdc_dictionary):
    assert 'aliquot.yaml' in pdc_dictionary.schema
    assert 'studyRunMetadata.yaml' not in pdc_dictionary.schema
