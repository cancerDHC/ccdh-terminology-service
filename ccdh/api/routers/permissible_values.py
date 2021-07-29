from typing import Optional, List

from fastapi import APIRouter
from fastapi_redis_cache import cache
from pydantic.main import BaseModel
from tccm_api.routers.concept_reference import ConceptReference

from ccdh.api.routers.models import NodeAttribute
from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph

mdr_graph = MdrGraph(neo4j_graph())


class PermissibleValue(BaseModel):
    pref_label: str
    node_attribute: Optional[str]
    meaning: Optional[ConceptReference]


PermissibleValue.update_forward_refs()


router = APIRouter(
    prefix='/values',
    tags=['Values in CRDC Node Models'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/{value}', response_model=List[PermissibleValue], response_model_exclude_unset=True)
@cache()
async def get_permissible_values(value: str) -> List[PermissibleValue]:
    return mdr_graph.find_permissible_values(value)
