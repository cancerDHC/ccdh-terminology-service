from ccdh.data_dictionaries.htan import *


def test_field_name():
    s = field_name('PREINVASIVE_MORPHOLOGY')
    assert s == 'PreinvasiveMorphology'


def test_htan():
    htan([])

