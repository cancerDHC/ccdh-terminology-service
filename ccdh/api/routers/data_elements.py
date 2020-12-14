from typing import Optional, List
from fastapi import APIRouter
from pydantic.main import BaseModel
from ccdh.config import neo4j_graph
from ccdh.mdr.mdr_graph import MdrGraph

mdr_graph = MdrGraph(neo4j_graph())


class DataElement(BaseModel):
    context: str
    entity: str
    attribute: str
    definition: Optional[str]
    data_element_concept: Optional['DataElementConcept']


from ccdh.api.routers.data_element_concepts import DataElementConcept
DataElement.update_forward_refs()


router = APIRouter(
    prefix='/data-elements',
    tags=['Data Elements'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/{context}/{entity}/{attribute}', response_model=List[DataElement])
async def get_data_elements(context: str, entity: str, attribute: str) -> List[DataElement]:
    return list(mdr_graph.find_data_elements(context, entity, attribute))


@router.get('/{context}/{entity}', response_model=List[DataElement])
async def get_data_elements(context: str, entity: str) -> List[DataElement]:
    return list(mdr_graph.find_data_elements(context, entity))


@router.get('/{context}', response_model=List[DataElement])
async def get_data_elements(context: str) -> List[DataElement]:
    return list(mdr_graph.find_data_elements(context))

