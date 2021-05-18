from typing import Optional, List
from fastapi import APIRouter
from pydantic.main import BaseModel
from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph

mdr_graph = MdrGraph(neo4j_graph())


class NodeAttribute(BaseModel):
    system: str
    entity: str
    attribute: str
    definition: Optional[str]
    harmonized_attribute: Optional['HarmonizedAttribute']
    permissible_values: Optional[List[str]]


from ccdh.api.routers.harmonized_attributes import HarmonizedAttribute
NodeAttribute.update_forward_refs()


router = APIRouter(
    prefix='/nodes',
    tags=['CRDC Node Models'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/{context}/{entity}/{attribute}', response_model=List[NodeAttribute], response_model_exclude_none=True)
async def get_data_elements(context: str, entity: str, attribute: str) -> List[NodeAttribute]:
    return mdr_graph.find_node_attributes_complete(context, entity, attribute)


@router.get('/{context}/{entity}', response_model=List[NodeAttribute], response_model_exclude_none=True)
async def get_data_elements(context: str, entity: str) -> List[NodeAttribute]:
    return mdr_graph.find_node_attributes_complete(context, entity)


@router.get('/{context}', response_model=List[NodeAttribute], response_model_exclude_none=True)
async def get_data_elements(context: str) -> List[NodeAttribute]:
    return mdr_graph.find_node_attributes_complete(context)

