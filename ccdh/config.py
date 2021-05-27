from functools import lru_cache
from py2neo import Graph
from pathlib import Path
from pydantic import BaseSettings
import logging

ROOT_DIR = Path(__file__).parent.parent

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)


def neo4j_graph() -> Graph:
    settings: Settings = get_settings()
    neo4j_bolt_uri = f'bolt://{settings.neo4j_host}:{settings.neo4j_bolt_port}'
    return Graph(neo4j_bolt_uri, auth=(settings.neo4j_username, settings.neo4j_password))


class Settings(BaseSettings):
    app_name: str = 'TCCM API'
    neo4j_username: str
    neo4j_password: str
    neo4j_host: str
    neo4j_bolt_port: str
    ccdhmodel_branch: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()

