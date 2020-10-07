from ccdh.gdc import *


def test_gdc_ncit_map():
    mappings = gdc_ncit_mappings()
    assert 'ann_arbor_b_symptoms' in mappings
    assert mappings['sample_type']['RNA'][0] == 'C812'
