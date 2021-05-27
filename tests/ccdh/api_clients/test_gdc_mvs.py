import pytest
from ccdh.api_clients.gdc_mvs import *


def test_search_term():
    ncit = search_term('cfDNA')
    assert len(ncit) == 2
