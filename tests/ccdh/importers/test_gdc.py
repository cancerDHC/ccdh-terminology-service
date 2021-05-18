import pytest
from ccdh.importers.gdc import GdcImporter


def test_gdc_entity_list():
    data_elements = GdcImporter.read_data_dictionary()
    assert 'GDC.Aliquot.analyte_type' in data_elements
    assert 'DNA' in data_elements['GDC.Aliquot.analyte_type']['permissible_values']


def test_read_ncit_mappings():
    mappings = GdcImporter.read_ncit_mappings()
    assert 'analyte_type' in mappings
    assert 'DNA' in mappings['analyte_type']
    assert 'C449' == mappings['analyte_type']['DNA'][0]
