from fastapi import APIRouter, Path, Request
from fastapi.responses import StreamingResponse
from typing import Optional, List, Dict

from fastapi.openapi.models import Response
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


class Mapping(BaseModel):
    subject_id: Optional[str]
    prefix_id: Optional[str]
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
    prefix='/harmonization',
    tags=['harmonization'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/data-elements/{context}/{entity}/{attribute}', response_model=List[DataElement])
def get_data_elements(context: str, entity: str, attribute: str) -> List[DataElement]:
    return list(mdr_graph.find_data_elements(context, entity, attribute))


@router.get('/data-elements/{context}/{entity}', response_model=List[DataElement])
def get_data_elements(context: str, entity: str) -> List[DataElement]:
    return list(mdr_graph.find_data_elements(context, entity))


@router.get('/data-elements/{context}', response_model=List[DataElement])
def get_data_elements(context: str) -> List[DataElement]:
    return list(mdr_graph.find_data_elements(context))


@router.get('/mapping/data-elements/{context}/{entity}/{attribute}', response_model=MappingSet,
            responses={
                200: {
                    "content": {
                        'text/tab-separated-values+sssom': {}
                    },
                    "description": "Return the JSON mapping set or a TSV file.",
                }
            })
def get_data_element_mapping(context: str, entity: str, attribute: str, request: Request) -> MappingSet:
    mapping_set = mdr_graph.find_mappings_of_data_element(context, entity, attribute, pagination=False)
    if request.headers['accept'] == 'text/tab-separated-values+sssom':
        return StreamingResponse(generate_sssom_tsv(MappingSet.parse_obj(mapping_set.__dict__)), media_type='text/tab-separated-values+sssom')
    else:
        return mapping_set.__dict__


@router.get('/mapping/data-element-concepts/{object_class}/{property}', response_model=MappingSet,
            responses={
                200: {
                    "content": {
                        'text/tab-separated-values+sssom': {}
                    },
                    "description": "Return the JSON mapping set or a TSV file.",
                }
            })
def get_data_element_concept_mapping(object_class: str, property: str, request: Request) -> MappingSet:
    mapping_set = mdr_graph.find_mappings_of_data_element_concept(object_class, property, pagination=False)
    if request.headers['accept'] == 'text/tab-separated-values+sssom':
        return StreamingResponse(generate_sssom_tsv(MappingSet.parse_obj(mapping_set.__dict__)), media_type='text/tab-separated-values+sssom')
    else:
        return mapping_set.__dict__


def generate_sssom_tsv(data):
    data_dict = dict(data)
    for key in data_dict:
        if key == 'mappings':
            row_num = 0
            for mapping in data_dict[key]:
                if row_num == 0:
                    yield '\t'.join(dict(mapping).keys()) + '\n'
                row_num += 1
                yield '\t'.join([str(i) if i else '' for i in dict(mapping).values()]) + '\n'
        elif key == 'curie_map':
            yield '#curie_map:\n'
            for curie, uri in data_dict[key].items():
                yield f'#  {curie}: "{uri}"\n'
        else:
            yield f'#{key}: {data_dict[key]}\n'



