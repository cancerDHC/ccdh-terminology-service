from ccdh.main import get_ncit_code


def test_get_ncit_code():
    cde_id = '5432508'
    get_ncit_code(cde_id)