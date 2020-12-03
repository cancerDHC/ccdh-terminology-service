import pytest
from ccdh.importers.gdc import GdcImporter


def test_gdc_entity_list():
    data_elements = GdcImporter.read_data_dictionary()
    assert 'GDC.Aliquot.analyte_type' in data_elements
    assert 'DNA' in data_elements['GDC.Aliquot.analyte_type']['permissible_values']