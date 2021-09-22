"""Models: classes and endpoints"""
from typing import Optional, List, Dict, Union

from fastapi import APIRouter
from ccdh.api.cache import cache
from pydantic.main import BaseModel
from starlette.responses import StreamingResponse
from tccm_api.routers.concept_reference import ConceptReference
from starlette.requests import Request
from datetime import date

from ccdh.api.routers.mappings import generate_sssom_tsv
from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph


mdr_graph = MdrGraph(neo4j_graph())


class Model(BaseModel):
    """Model"""
    name: str
    description: Optional[str]


class Entity(BaseModel):
    """Entity"""
    name: str
    description: Optional[str]


class Attribute(BaseModel):
    """Attribute"""
    name: str


class Enumeration(BaseModel):
    """Enumeration"""
    name: str


class Mapping(BaseModel):
    """Mapping
        TODO: @Dazhi: This class is exactly the same as the 'Mapping' class
        in the 'models' module. - jef 2021/07/30
    """
    # subject_id: Optional[str]
    subject_match_field: str
    subject_label: str
    predicate_id: Optional[str]
    object_id: Optional[str]
    object_label: Optional[str]
    object_match_field: Optional[str]
    creator_id: Optional[str]
    comment: Optional[str]
    mapping_date: Optional[date]


class MappingSet(BaseModel):
    """Mapping set"""
    creator_id: str
    license: str
    mapping_provider: str
    curie_map: Dict[str, str] = {
        'NCIT': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#',
    }
    mappings: List[Mapping] = []


class NodeAttribute(BaseModel):
    """Node attribute"""
    system: str
    entity: str
    attribute: str
    definition: Optional[str]
    harmonized_attribute: Optional['HarmonizedAttribute']
    permissible_values: Optional[List[str]]


class HarmonizedAttribute(BaseModel):
    """Harmonized attribute"""
    system: str
    entity: str
    attribute: str
    definition: Optional[str]
    node_attributes: Optional[List['NodeAttribute']]
    concept_references: Optional[List[ConceptReference]]


NodeAttribute.update_forward_refs()
HarmonizedAttribute.update_forward_refs()


router = APIRouter(
    prefix='/models',
    tags=['CRDC-H and CRDC Node Models'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/', response_model=List[Model],
            description="Lists the models (original node models and harmonized models)",
            response_model_exclude_none=True,
            operation_id='get_models',
            responses={
                "200": {
                    "links": {
                        "Model": {
                            "operationId": "get_model",
                            "parameters": {
                                "model": "$resonse.body#/{index}/name"
                            }
                        }
                    }
                }
            })
@cache()
async def get_models():
    """Get models"""
    models = mdr_graph.list_models()
    res = []
    for model in models:
        res.append(Model(name=model))
    return res


@router.get('/{model}', response_model=Model, operation_id='get_model', response_model_exclude_none=True,
            responses={
                "200": {
                    "links": {
                        "Entities": {
                            "operationId": "get_model_entities",
                            "parameters": {
                                "model": "$request.path.model"
                            }
                        }
                    }
                }
            })
@cache()
async def get_model(model: str):
    """Get a single model"""
    return Model(name=model)


@router.get('/{model}/entities', response_model=List[Entity], operation_id='get_model_entities',
            response_model_exclude_none=True,
            responses={
                "200": {
                    "links": {
                        "Entity": {
                            "operationId": "get_model_entity",
                            "parameters": {
                                "model": "$resonse.body#/{index}/name",
                                "entity": "$response.body#/{index}/name"
                            }
                        }
                    }
                }
            })
@cache()
async def get_model_entities(model: str):
    """Get a model's entities"""
    entities = mdr_graph.list_entities(model)
    res = []
    for entity in entities:
        res.append(Entity(name=entity))
    return res


@router.get('/{model}/entities/{entity}', response_model=Entity, operation_id='get_model_entity',
            response_model_exclude_none=True,
            responses={
                "200": {
                    "links": {
                        "Attributes": {
                            "operationId": "get_model_entity_attributes",
                            "parameters": {
                                "model": "$request.path.model",
                                "entity": "$request.path.entity"
                            }
                        }
                    }
                }
            })
@cache()
async def get_model_entity(model: str, entity: str):
    """Get an entity from a model"""
    # TODO: iterate over entities and return the entity matching 'entity'?
    # ... or is this correct?
    # entities = mdr_graph.list_entities(model)
    return Entity(name=entity)


@router.get('/{model}/entities/{entity}/attributes', response_model=List[Attribute],
            operation_id='get_model_entity_attributes', response_model_exclude_none=True,
            responses={
                "200": {
                    "links": {
                        "Attribute": {
                            "operationId": "get_model_entity_attribute",
                            "parameters": {
                                "model": "$request.path.model",
                                "entity": "$request.path.entity",
                                "attribute": "$response.body#/{index}/name"
                            }
                        }
                    }
                }
            })
@cache()
async def get_model_entity_attributes(model: str, entity: str):
    """Get an all entities and their attributes"""
    models = mdr_graph.list_attributes(model, entity)
    res = []
    for model in models:
        res.append(Attribute(name=model))
    return res


@router.get('/{model}/entities/{entity}/attributes/{attribute}',
            # response_model=Union[HarmonizedAttribute, NodeAttribute],
            # response_model_exclude_unset=True,
            operation_id='get_model_entity_attribute',
            responses={
                "200": {
                    "links": {
                        "Attribute": {
                            "operationId": "get_model_entity_attribute",
                            "parameters": {
                                "model": "$request.path.model",
                                "entity": "$request.path.entity",
                                "attribute": "$request.path.attribute"
                            }
                        }
                    }
                }
            })
@cache()
async def get_model_entity_attribute(
        model: str, entity: str, attribute: str
) -> Union[HarmonizedAttribute, NodeAttribute, Dict]:
    """Get an entity's attributes"""
    if model in mdr_graph.list_harmonized_models():
        result = mdr_graph.find_harmonized_attributes_complete(model, entity, attribute)
    else:
        result = mdr_graph.find_node_attributes_complete(model, entity, attribute)
    return result[0] if result else {}


@router.get('/{model}/entities/{entity}/attributes/{attribute}/enumerations',
            response_model=List[Enumeration],
            response_model_exclude_unset=True,
            operation_id='get_model_entity_attribute_enums',
            responses={
                "200": {
                    "links": {
                        "Enumeration": {
                            "operationId": "get_enumeration",
                            "parameters": {
                                "name": "$response.body#/{index}/name"
                            }
                        }
                    }
                }
            })
@cache()
async def get_model_entity_attribute_enums(model: str, entity: str, attribute: str) -> List[Enumeration]:
    """Get an enumeration of entity attributes"""
    return [Enumeration(name=model + '.' + entity + '.' + attribute)]


@router.get('/{model}/entities/{entity}/attributes/{attribute}/mappings',
            response_model=MappingSet,
            response_model_exclude_unset=True,
            operation_id='get_model_entity_attribute_mappings',
            responses={
                200: {
                    "content": {
                        'text/tab-separated-values+sssom': {}
                    },
                    "description": "Return the JSON mapping set or a TSV file.",
                }
            })
@cache()
async def get_model_entity_attribute_mappings(request: Request, model: str, entity: str, attribute: str) -> MappingSet:
    """Get mappings for a given entity attribute"""
    if model in mdr_graph.list_harmonized_models():
        mapping_set = mdr_graph.find_mappings_of_harmonized_attribute(model, entity, attribute, pagination=False)
    else:
        mapping_set = mdr_graph.find_mappings_of_node_attribute(model, entity, attribute, pagination=False)
    if request.headers['accept'] == 'text/tab-separated-values+sssom':
        return StreamingResponse(
            generate_sssom_tsv(MappingSet.parse_obj(mapping_set.__dict__)),
            media_type='text/tab-separated-values+sssom')
    else:
        return mapping_set.__dict__
