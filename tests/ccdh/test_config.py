from ccdh.config import get_settings


def test_config():
    settings = get_settings()
    assert settings.neo4j_bolt_port is not None
