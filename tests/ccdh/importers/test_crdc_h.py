from linkml.utils.schemaloader import SchemaLoader
from linkml.utils.yamlutils import YAMLRoot

from ccdh.config import CDM_GOOGLE_SHEET_ID
from ccdh.importers.crdc_h import CrdcHImporter
import requests
import pytest
from linkml.loaders import yaml_loader


@pytest.fixture
def ccdh_model_yaml():
    yaml_url = 'https://raw.githubusercontent.com/cancerDHC/ccdhmodel/7d377740f17ad0cb1bf716483f64a55fd6fabf34/src/schema/ccdhmodel.yaml'
    r = requests.get(yaml_url)
    if r.status_code == 200:
        return r.content
    else:
        raise ValueError('Failed to fetch yaml from ' + yaml_url)


def test_read_data_element_concepts():
    decs = CrdcHImporter.read_harmonized_attributes_from_google_sheet(sheet_id=CDM_GOOGLE_SHEET_ID, ranges='MVPv0')
    assert 'CDM.Research Subject.primary_disease_type' in decs
    assert 'GDC.Analyte.analyte_type' in decs['CDM.Specimen.analyte_type']['node_attributes']


def test_read_crdch(ccdh_model_yaml):
    attributes = CrdcHImporter.read_harmonized_attributes(ccdh_model_yaml)
    assert 'CRDC-H.Specimen.analyte_type' in attributes

