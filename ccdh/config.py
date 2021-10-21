"""Config"""
import logging
import os
from functools import lru_cache
from py2neo import Graph
from pathlib import Path
from pydantic import BaseSettings, ValidationError
from typing import Optional


ROOT_DIR = Path(__file__).parent.parent

# ENV_NAME_ENV_FILE_MAP = {
#     'production': '.env.prod',
#     'test': '.env.test',
#     'development': '.env.dev'
# }

# noinspection PyArgumentList
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)


def neo4j_graph() -> Graph:
    """neo4j_graph"""
    settings: Settings = get_settings()
    neo4j_bolt_uri = f'bolt://{settings.neo4j_host}:{settings.neo4j_bolt_port}'
    return Graph(neo4j_bolt_uri, auth=(settings.neo4j_username, settings.neo4j_password))


class Settings(BaseSettings):
    """Settings"""
    app_name: str = 'TCCM API'
    neo4j_username: str
    neo4j_password: str
    neo4j_host: str
    neo4j_bolt_port: str
    redis_url: str
    docker_user_token_limited: str
    ccdhmodel_branch: Optional[str] = 'main'
    environment_name: Optional[str] = 'production'


@lru_cache()
def get_settings():
    """get_settings"""
    # env_name = os.getenv('ENVIRONMENT_NAME', 'production')
    # env_file_path = os.path.join(ROOT_DIR, ENV_NAME_ENV_FILE_MAP[env_name])
    env_file_path = os.path.join(ROOT_DIR, '.env')
    try:
        settings = Settings(_env_file=env_file_path)
        return settings
    except ValidationError as err:
        print(str(err))
        print('Env files not found?:')
        print('env_file_path:', env_file_path)
        from pprint import pprint
        pprint(os.listdir(ROOT_DIR))
        print('env file exists?:', '.env' in os.listdir())
        with open(env_file_path, 'r') as file:
            print(file.read())
        raise FileNotFoundError(';(')
