from typing import Optional, List
from fastapi import APIRouter
from pydantic.main import BaseModel
from tccm_api.routers.concept_reference import ConceptReference

from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph


mdr_graph = MdrGraph(neo4j_graph())


class HarmonizedAttribute(BaseModel):
    system: str
    entity: str
    attribute: str
    definition: Optional[str]
    node_attributes: Optional[List['NodeAttribute']]
    concept_references: Optional[List[ConceptReference]]


from ccdh.api.routers.node_attributes import NodeAttribute
HarmonizedAttribute.update_forward_refs()


router = APIRouter(
    prefix='/crdc-h',
    tags=['CRDC-H Models'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/{system}/{entity}/{attribute}', response_model=List[HarmonizedAttribute], response_model_exclude_unset=True)
async def get_harmonized_attributes(system: str, entity: str, attribute: str) -> List[HarmonizedAttribute]:
    return mdr_graph.find_harmonized_attributes_complete(system, entity, attribute)

