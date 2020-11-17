from flask import current_app, g
from py2neo import Graph
from ccdh.config import neo4j_graph


def get_neo4j_graph() -> Graph:
    if 'neo4j_graph' not in g:
        g.neo4j_graph = neo4j_graph()
    return g.neo4j_graph
