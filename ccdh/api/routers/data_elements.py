from fastapi import APIRouter
from typing import Optional, List, Dict

from pydantic.main import BaseModel
from datetime import date

from ccdh.config import neo4j_graph
from ccdh.mdr.mdr_graph import MdrGraph

mdr_graph = MdrGraph(neo4j_graph())


class DataElement(BaseModel):
    context: str
    entity: str
    attribute: str
    definition: Optional[str]


class DataElementConcept(BaseModel):
    context: str
    object_class: str
    property: str
    definition: Optional[str]


class Mapping(BaseModel):
    subject_id: Optional[str]
    predicate_id: Optional[str]
    object_id: Optional[str]
    subject_label: str
    subject_match_field: str
    object_label: Optional[str]
    object_match_field: Optional[str]
    creator_id: Optional[str]
    comment: Optional[str]
    mapping_date: Optional[date]


class MappingSet(BaseModel):
    creator_id: str
    license: str
    mapping_provider: str
    curie_map: Dict[str, str] = {
        'NCIT': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#',
        'CS:NCIT': '',
    }
    mappings: List[Mapping] = []


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

