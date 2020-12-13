from rfc3986 import uri_reference, is_valid_uri
from urllib.parse import unquote, unquote_plus
from ccdh.api.namespaces import NAMESPACES


def decode_uri(uri: str) -> str:
    if is_valid_uri(uri, require_scheme=True, require_authority=True, require_path=True):
        return uri

    unq_uri = unquote(uri)
    if is_valid_uri(unq_uri, require_scheme=True, require_authority=True, require_path=True):
        return unq_uri

    unq_uri = unquote_plus(uri)
    if is_valid_uri(unq_uri, require_scheme=True, require_authority=True, require_path=True):
        return unq_uri

    exp_uri = expand_curie(uri, NAMESPACES)
    if is_valid_uri(exp_uri, require_scheme=True, require_authority=True, require_path=True):
        return exp_uri

    unq_uri = unquote(exp_uri)
    if is_valid_uri(unq_uri, require_scheme=True, require_authority=True, require_path=True):
        return unq_uri

    return uri


def expand_curie(curie: str, curie_maps) -> str:
    """
    Expands a CURIE/identifier to a URI
    """
    if curie.find(":") == -1:
        return curie
    [prefix, local_id] = curie.split(":", 1)
    if prefix.upper() in curie_maps:
        return curie_maps[prefix] + local_id
    return curie
