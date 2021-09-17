from ccdh.importers.crdc_h import CrdcHImporter
import requests
import pytest
from ccdh.config import get_settings


@pytest.fixture
def ccdh_model_yaml():
    settings = get_settings()
    yaml_url = f'https://raw.githubusercontent.com/cancerDHC/ccdhmodel/{settings.ccdhmodel_branch}/model/schema/crdch_model.yaml'
    r = requests.get(yaml_url)
    if r.status_code == 200:
        return r.content
    else:
        raise ValueError('Failed to fetch yaml from ' + yaml_url)


def test_read_crdch(ccdh_model_yaml):
    attributes = CrdcHImporter.read_harmonized_attributes(ccdh_model_yaml)
    assert 'CRDC-H.Specimen.analyte_type' in attributes

