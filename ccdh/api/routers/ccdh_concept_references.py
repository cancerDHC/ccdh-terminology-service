"""CCDH Concept References: classes and endpoints"""
from fastapi import Request
from ccdh.api.cache import cache
from starlette.responses import StreamingResponse
from tccm_api.routers import concept_reference

from ccdh.api.routers.mappings import generate_sssom_tsv
from ccdh.api.routers.models import MappingSet
from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph

# TODO: Architecturally, why is 'concept_reference' in TCCM-API when so much else
#  ...is in CCDH terminology service? What is the logic behind what is and isn't
#  ...in TCCM? - joeflack4 2021/10/27
router = concept_reference.router
mdr_graph = MdrGraph(neo4j_graph())


@router.get(
    '/{curie}/mappings',
    description='An SSSOM TSV file depending on request headers, otherwise a list of mappings',
    response_model=MappingSet)
@cache()
def get_concept_reference_mappings(curie: str, request: Request):
    """Get concept reference mappings"""
    mapping_set = mdr_graph.find_mappings_of_concept_reference(curie)
    if request.headers['accept'] == 'text/tab-separated-values+sssom':
        return StreamingResponse(
            generate_sssom_tsv(MappingSet.parse_obj(mapping_set.__dict__)),
            media_type='text/tab-separated-values+sssom')
    else:
        return mapping_set.__dict__
