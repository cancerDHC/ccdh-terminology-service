import pytest
from ccdh.data_dictionaries.pdc import PDCDictionary, PDC_ROOT

#
# @pytest.fixture
# def pdc_dictionary():
#     return PDCDictionary(root_dir=PDC_ROOT)
#
#
# def test_read_pdc(pdc_dictionary):
#     assert 'aliquot.yaml' in pdc_dictionary.schema
#     assert 'studyRunMetadata.yaml' not in pdc_dictionary.schema
