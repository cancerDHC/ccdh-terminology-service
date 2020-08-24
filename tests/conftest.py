import pytest
from ccdh.model.cdm_biolinkml_loader import load_ccdh_specimen
from typing import List
from biolinkml.meta import SchemaDefinition
from biolinkml.utils.yamlutils import as_yaml


@pytest.fixture
def specimen():
    return load_ccdh_specimen()


