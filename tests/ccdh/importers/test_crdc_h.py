from ccdh.config import CDM_GOOGLE_SHEET_ID
from ccdh.importers.crdc_h import CrdcHImporter


def test_read_data_element_concepts():
    decs = CrdcHImporter.read_harmonized_attributes(sheet_id=CDM_GOOGLE_SHEET_ID, ranges='MVPv0')
    assert 'CDM.Research Subject.primary_disease_type' in decs
    assert 'GDC.Analyte.analyte_type' in decs['CDM.Specimen.analyte_type']['node_attributes']