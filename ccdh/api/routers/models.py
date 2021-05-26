from typing import Optional, List, Dict, Union
from fastapi import APIRouter
from pydantic.main import BaseModel
from tccm_api.routers.concept_reference import ConceptReference
from starlette.requests import Request

from ccdh.config import neo4j_graph
from ccdh.db.mdr_graph import MdrGraph


mdr_graph = MdrGraph(neo4j_graph())


class Model(BaseModel):
    name: str
    description: Optional[str]


class Entity(BaseModel):
    name: str
    description: Optional[str]


class Attribute(BaseModel):
    name: str


class HarmonizedAttribute(BaseModel):
    system: str
    entity: str
    attribute: str
    definition: Optional[str]
    mapped_attributes: Optional[List['NodeAttribute']]
    concept_references: Optional[List[ConceptReference]]


from ccdh.api.routers.node_attributes import NodeAttribute
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
async def get_models(request: Request):
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
async def get_model(model: str):
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
async def get_model_entities(request: Request, model: str):
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
async def get_model_entity(model: str, entity: str):
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
async def get_model_entity_attributes(model: str, entity: str):
    models = mdr_graph.list_attributes(model, entity)
    res = []
    for model in models:
        res.append(Attribute(name=model))
    return res


@router.get('/{model}/entities/{entity}/attributes/{attribute}',
            response_model=Union[HarmonizedAttribute, NodeAttribute],
            response_model_exclude_unset=True,
            operation_id='get_model_entity_attribute')
async def get_model_entity_attribute(model: str, entity: str, attribute: str) -> Union[HarmonizedAttribute, NodeAttribute]:
    if model in ['GDC', 'PDC']:
        return mdr_graph.find_node_attributes_complete(model, entity, attribute)[0]
    else:
        return mdr_graph.find_harmonized_attributes_complete(model, entity, attribute)[0]

