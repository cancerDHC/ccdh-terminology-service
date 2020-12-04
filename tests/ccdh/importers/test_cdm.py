from ccdh.config import CDM_GOOGLE_SHEET_ID
from ccdh.importers.cdm import CdmImporter


def test_read_data_element_concepts():
    decs = CdmImporter.read_data_element_concepts(sheet_id=CDM_GOOGLE_SHEET_ID, ranges='MVPv0')
    assert 'CDM.Research Subject.primary_disease_type' in decs
    assert 'GDC.Analyte.analyte_type' in decs['CDM.Specimen.analyte_type']['data_elements']