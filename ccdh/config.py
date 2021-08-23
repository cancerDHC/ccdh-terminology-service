import logging
import os
from functools import lru_cache
from py2neo import Graph
from pathlib import Path
from pydantic import BaseSettings
from typing import Optional

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
    redis_url: str
    docker_user_token_limited: str
    ccdhmodel_branch: Optional[str] = 'main'

    # @Dazhi: I was having difficulty fetching settings consistently from different
    # files. I think this pathing is better than us needing to make symlinks and
    # populate .env files in different directories. If you agree, let's remove
    # these commented lines below. - Joe 2021/08/23
    # class Config:
    #     env_file = os.path.join(os.path.realpath(__file__), '..', 'docker' '.env')


@lru_cache()
def get_settings():
    env_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '.env')
    return Settings(_env_file=env_file_path)
