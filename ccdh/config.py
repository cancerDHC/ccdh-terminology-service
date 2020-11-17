import configparser
from py2neo import Graph
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent


def config() -> dict:
    cfg = configparser.ConfigParser()
    cfg.read(ROOT_DIR / 'config.ini')
    return cfg


def neo4j_graph() -> Graph:
    cfg = config()
    bolt_uri = cfg.get('neo4j', 'bolt_uri')
    user = cfg.get('neo4j', 'user')
    password = cfg.get('neo4j', 'password')
    return Graph(bolt_uri, auth=(user, password))


DEFAULT_PAGE_SIZE = int(config()['pagination']['page_size'])
MAX_PAGE_SIZE = int(config()['pagination']['max_page_size'])