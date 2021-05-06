from typing import Optional, List
from fastapi import APIRouter
from pydantic.main import BaseModel
from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph

mdr_graph = MdrGraph(neo4j_graph())


class DataElementConcept(BaseModel):
    context: str
    object_class: str
    property: str
    definition: Optional[str]
    data_elements: Optional[List['DataElement']]
    value_meanings: Optional[List['ValueMeaning']]


from ccdh.api.routers.data_elements import DataElement
from ccdh.api.routers.value_meanings import ValueMeaning
DataElementConcept.update_forward_refs()


router = APIRouter(
    prefix='/crdc-h',
    tags=['CRDC-H Models'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/{context}/{entity}/{attribute}', response_model=List[DataElementConcept], response_model_exclude_unset=True)
async def get_data_element_concepts(context: str, entity: str, attribute: str) -> List[DataElementConcept]:
    return mdr_graph.find_data_element_concepts_complete(context, entity, attribute)

