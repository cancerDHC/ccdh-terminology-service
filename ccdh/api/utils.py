from rfc3986 import uri_reference, is_valid_uri
from urllib.parse import unquote, unquote_plus
from ccdh.namespaces import NAMESPACES
from prefixcommons.curie_util import contract_uri


def decode_uri(uri: str) -> str:
    if is_valid_uri(uri, require_scheme=True, require_authority=True, require_path=True):
        return uri

    unq_uri = unquote(uri)
    if is_valid_uri(unq_uri, require_scheme=True, require_authority=True, require_path=True):
        return unq_uri

    unq_uri = unquote_plus(uri)
    if is_valid_uri(unq_uri, require_scheme=True, require_authority=True, require_path=True):
        return unq_uri

    exp_uri = curie_to_uri(uri, NAMESPACES)
    if is_valid_uri(exp_uri, require_scheme=True, require_authority=True, require_path=True):
        return exp_uri

    unq_uri = unquote(exp_uri)
    if is_valid_uri(unq_uri, require_scheme=True, require_authority=True, require_path=True):
        return unq_uri

    return uri


def curie_to_uri(curie: str, curie_map=NAMESPACES) -> str:
    """
    Expands a CURIE/identifier to a URI
    """
    if curie.find(":") == -1:
        return curie
    [prefix, local_id] = curie.split(":", 1)
    if prefix.upper() in curie_map:
        return curie_map[prefix] + local_id
    return curie


def uri_to_curie(uri: str, curie_map=NAMESPACES) -> str:
    curies = contract_uri(uri, [curie_map], shortest=True)
    if curies:
        return curies[0]
    else:
        return uri
