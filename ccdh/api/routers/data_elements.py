from typing import Optional, List
from fastapi import APIRouter
from pydantic.main import BaseModel
from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph

mdr_graph = MdrGraph(neo4j_graph())


class DataElement(BaseModel):
    context: str
    entity: str
    attribute: str
    definition: Optional[str]
    data_element_concept: Optional['DataElementConcept']
    permissible_values: Optional[List[str]]


from ccdh.api.routers.data_element_concepts import DataElementConcept
DataElement.update_forward_refs()


router = APIRouter(
    prefix='/nodes',
    tags=['CRDC Node Models'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/{context}/{entity}/{attribute}', response_model=List[DataElement], response_model_exclude_none=True)
async def get_data_elements(context: str, entity: str, attribute: str) -> List[DataElement]:
    return mdr_graph.find_data_elements_complete(context, entity, attribute)


@router.get('/{context}/{entity}', response_model=List[DataElement], response_model_exclude_none=True)
async def get_data_elements(context: str, entity: str) -> List[DataElement]:
    return mdr_graph.find_data_elements_complete(context, entity)


@router.get('/{context}', response_model=List[DataElement], response_model_exclude_none=True)
async def get_data_elements(context: str) -> List[DataElement]:
    return mdr_graph.find_data_elements_complete(context)

