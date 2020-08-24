import pytest
from biolinkml.utils.schemaloader import SchemaLoader


def test_specimen(specimen, caplog):
    loader = SchemaLoader(data=specimen, logger=caplog)
    assert loader.schema.name == 'Specimen'
    assert 'ADM:Sample' in loader.schema.mappings
    assert len(loader.schema.classes) == 1
