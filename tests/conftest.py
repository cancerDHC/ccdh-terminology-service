import sys
from pathlib import Path

import pytest
import requests
from requests.exceptions import ConnectionError
from py2neo import Graph

from ccdh.config import get_settings


def is_responsive(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


@pytest.fixture(scope='session')
def neo4j_graph(docker_ip, docker_services):
    settings = get_settings()
    port = docker_services.port_for('ccdh-neo4j', 7474)
    url = f'http://{docker_ip}:{port}'
    docker_services.wait_until_responsive(
        timeout=60.0, pause=0.1, check=lambda: is_responsive(url)
    )
    bolt_port = docker_services.port_for('ccdh-neo4j', 7687)
    bolt_url = f'bolt://{docker_ip}:{bolt_port}'
    graph = Graph(bolt_url, auth=(settings.neo4j_username, settings.neo4j_password))
    yield graph
