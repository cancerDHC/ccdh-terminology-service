from fastapi import APIRouter
from typing import Optional, List, TYPE_CHECKING

from pydantic.main import BaseModel
from datetime import date

from ccdh.api.utils import decode_uri
from ccdh.config import neo4j_graph
from ccdh.mdr.mdr_graph import MdrGraph

mdr_graph = MdrGraph(neo4j_graph())


class ValueMeaning(BaseModel):
    notation: str
    scheme: str
    uri: str
    pref_label: str
    representations: Optional[List[str]]


router = APIRouter(
    prefix='/value-meanings',
    tags=['Value Meanings (Concepts)'],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get('/{uri}', response_model=ValueMeaning)
async def get_value_meaning(uri: str) -> ValueMeaning:
    uri = decode_uri(uri)
    node = mdr_graph.find_value_meaning(uri)
    return node
